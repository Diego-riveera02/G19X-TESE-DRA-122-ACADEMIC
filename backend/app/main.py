from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import os
import json
import smtplib
import random
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from . import models, schemas
from .database import engine, get_db, SessionLocal

# Fuerza a Python a leer la llave nueva
load_dotenv(override=True, encoding='utf-8')
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obligamos a Groq a usar la llave del archivo .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 

SECRET_KEY = (os.getenv("SECRET_KEY") or "").strip()

if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Debes configurar SECRET_KEY con al menos 32 caracteres."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =================================================================
#                MODELOS EXTRAS PARA REQUESTS
# =================================================================
class ChatRequest(BaseModel):
    anomaly_id: int
    pregunta: str
    contexto_anomalia: str

class VerificarRequest(BaseModel):
    correo: str
    codigo: str

class SolicitarCodigoRequest(BaseModel):
    correo: str

class RecuperarRequest(BaseModel):
    correo: str
    codigo: str
    nueva_password: str

# =================================================================
#                GESTOR DE WEBSOCKETS
# =================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/anomalias")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =================================================================
#                FUNCIONES DE UTILIDAD Y SEGURIDAD
# =================================================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.correo == correo).first()
    if user is None:
        raise credentials_exception
    return user

def get_color(estado):
    if estado == "Critico": return "#E63946"
    if estado == "Alerta": return "#D4A017"
    return "#4BB543"

# =================================================================
#                SISTEMA DE CORREOS E IA
# =================================================================
def enviar_correo_verificacion(destinatario: str, codigo: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario 
        msg['Subject'] = "🔒 Código de Verificación - PluriOne"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">
                <div style="border: 2px solid #E5B80B; border-radius: 8px; padding: 30px; background-color: #1a1a1d; text-align: center;">
                    <h2 style="color: #E5B80B; margin-top: 0;">VERIFICACIÓN DE CUENTA PLURIONE</h2>
                    <p style="font-size: 16px;">Para completar tu solicitud, ingresa el siguiente código de 6 dígitos en la plataforma:</p>
                    <div style="background-color: #0b0c10; padding: 15px; margin: 20px 0; border-radius: 8px; display: inline-block;">
                        <h1 style="color: #E63946; margin: 0; letter-spacing: 5px;">{codigo}</h1>
                    </div>
                    <p style="font-size: 12px; color: #888;">Si tú no solicitaste este acceso, puedes ignorar este mensaje.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error al enviar código de verificación: {e}")

def enviar_alerta_correo_consolidado(destinatario: str, lat_v: str, lat_s: str, cal_v: str, cal_s: str, fal_v: str, fal_s: str, diag_general: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario 
        msg['Subject'] = "🚨 REPORTE CONSOLIDADO DE INFRAESTRUCTURA - PluriOne"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">
                <div style="border: 2px solid #8B0000; border-radius: 8px; padding: 20px; background-color: #1a1a1d;">
                    <h2 style="color: #E63946; margin-top: 0;">SISTEMA CENTRAL PLURIONE - REPORTE DE ESTADO</h2>
                    <p>Se ha registrado un evento crítico. A continuación se presenta el estado consolidado de los tres componentes del sistema:</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #111217;">
                        <tr style="background-color: #333; color: #fff;">
                            <th style="padding: 10px; text-align: left;">Componente / Métrica</th>
                            <th style="padding: 10px; text-align: left;">Valor</th>
                            <th style="padding: 10px; text-align: left;">Estado</th>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Latencia de Red (API Gateway)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{lat_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(lat_s)};">{lat_s}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Calidad de Datos (Ventas MX)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{cal_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(cal_s)};">{cal_s}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Tasa de Fallos (Migración AWS)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{fal_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(fal_s)};">{fal_s}</td>
                        </tr>
                    </table>

                    <h4 style="color: #E5B80B; margin-top: 25px; margin-bottom: 5px;">DIAGNÓSTICO DE CAUSA RAÍZ (J.A.R.V.I.S.)</h4>
                    <div style="background-color: rgba(212, 160, 23, 0.1); border-left: 3px solid #E5B80B; padding: 12px; color: #e0e0e0; line-height: 1.5;">
                        {diag_general}
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error al enviar correo: {e}")

def generar_recomendacion_ia(pipeline_name: str, metric_type: str, value: float) -> str:
    prompt = f"Anomalía en {pipeline_name}, Métrica: {metric_type}, Valor: {value}. Explica brevemente por qué representa un riesgo técnico."
    # CAMBIO FINAL: Nombres exactos actualizados
    for modelo in ["openai/gpt-oss-20b", "qwen/qwen3-32b"]:
        try:
            chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=modelo)
            contenido = chat_completion.choices[0].message.content
            if contenido: return contenido
        except Exception as e: 
            print(f"Error IA en simulador ({modelo}): {e}")
            continue
    return f"Revisar anomalía en {pipeline_name}."

# =================================================================
#                SIMULADOR DE INGESTA AUTOMATICA (NIVEL INGENIERÍA)
# =================================================================
async def generar_telemetria_automatica():
    """Motor que genera métricas continuas en segundo plano."""
    while True:
        await asyncio.sleep(5)  # Espera 5 segundos entre cada inyección de datos
        
        # Solo inyecta datos si hay alguien conectado al WebSocket
        if not manager.active_connections:
            continue
            
        pipelines = ["API Gateway Core", "Pipeline Ventas MX", "Migración AWS S3", "Sync PostgreSQL"]
        metricas = [
            ("latencia_ms", 50.0, 900.0, "ms"),
            ("datos_corruptos_%", 0.0, 15.0, "%"),
            ("tasa_fallos_%", 0.0, 25.0, "%")
        ]
        
        pipe = random.choice(pipelines)
        m_tipo, min_v, max_v, unidad = random.choice(metricas)
        valor_generado = round(random.uniform(min_v, max_v), 2)
        
        estado = "Normal"
        if valor_generado > (max_v * 0.75):
            estado = "Critico"
        elif valor_generado > (max_v * 0.45):
            estado = "Alerta"

        # Abre una sesión a la BD de forma independiente para la tarea en segundo plano
        db = SessionLocal()
        try:
            # Selecciona un usuario "Admin" o el primero para asignarle la métrica
            user = db.query(models.User).first()
            if not user:
                continue

            # Genera anomalía solo si es Crítico o Alerta
            recomendacion = "Operación normal."
            if estado != "Normal":
                recomendacion = generar_recomendacion_ia(pipe, m_tipo, valor_generado)

            db_anomalia = models.AnomalyLog(
                pipeline_name=pipe,
                metric_type=m_tipo,
                value=valor_generado,
                status=estado,
                ai_recommendation=recomendacion,
                user_id=user.id
            )
            db.add(db_anomalia)
            db.commit()
            db.refresh(db_anomalia)

            # Envía el dato en tiempo real a todos los clientes (React)
            mensaje_ws = json.dumps({
                "id": db_anomalia.id,
                "pipeline_name": db_anomalia.pipeline_name,
                "metric_type": db_anomalia.metric_type,
                "value": db_anomalia.value,
                "status": db_anomalia.status,
                "ai_recommendation": db_anomalia.ai_recommendation
            })
            await manager.broadcast(mensaje_ws)
        except Exception as e:
            print(f"Error en simulador: {e}")
        finally:
            db.close()

# Inicia el motor automático al prender FastAPI
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generar_telemetria_automatica())

# =================================================================
#                ENDPOINTS DE AUTENTICACIÓN
# =================================================================
@app.post("/registro/", response_model=schemas.UserResponse)
def registrar_usuario(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.correo == user.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    codigo_secreto = str(random.randint(100000, 999999))
    
    nuevo_usuario = models.User(
        nombre_completo=user.nombre_completo, 
        correo=user.correo, 
        telefono=user.telefono, 
        hashed_password=get_password_hash(user.password),
        codigo_verificacion=codigo_secreto,
        is_active=False 
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    background_tasks.add_task(enviar_correo_verificacion, user.correo, codigo_secreto)
    return nuevo_usuario

@app.post("/verificar/")
def verificar_codigo(req: VerificarRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == req.correo).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.is_active:
        return {"status": "El usuario ya estaba verificado"}
    if user.codigo_verificacion != req.codigo:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    
    user.is_active = True
    user.codigo_verificacion = None
    db.commit()
    return {"status": "Cuenta verificada con éxito"}

@app.post("/solicitar-recuperacion/")
def solicitar_recuperacion(req: SolicitarCodigoRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == req.correo).first()
    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta con este correo")
    
    codigo_secreto = str(random.randint(100000, 999999))
    user.codigo_verificacion = codigo_secreto
    db.commit()
    
    background_tasks.add_task(enviar_correo_verificacion, user.correo, codigo_secreto)
    return {"status": "Código de recuperación enviado al correo"}

@app.post("/recuperar-password/")
def recuperar_password(req: RecuperarRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == req.correo).first()
    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta con este correo")
    
    if not user.codigo_verificacion or user.codigo_verificacion != req.codigo:
        raise HTTPException(status_code=400, detail="Código incorrecto o expirado")
    
    user.hashed_password = get_password_hash(req.nueva_password)
    user.codigo_verificacion = None 
    db.commit()
    return {"status": "Contraseña actualizada exitosamente"}

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tu cuenta aún no está verificada. Revisa tu correo o verifica tu cuenta.")
        
    token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer", "nombre": user.nombre_completo, "correo": user.correo}

# =================================================================
#                ENDPOINTS DE LECTURA E HISTORIAL
# =================================================================
@app.get("/anomalias/", response_model=list[schemas.AnomalyLogResponse])
def read_anomalies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.AnomalyLog).filter(models.AnomalyLog.user_id == current_user.id).offset(skip).limit(limit).all()

@app.delete("/anomalias/")
def clear_anomalies(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db.query(models.AnomalyLog).filter(models.AnomalyLog.user_id == current_user.id).delete()
    db.commit()
    return {"status": "Historial borrado exitosamente"}

@app.post("/chat/")
def chat_causa_raiz(chat_req: ChatRequest, current_user: models.User = Depends(get_current_user)):
    contexto = chat_req.contexto_anomalia if chat_req.contexto_anomalia else "Sin diagnóstico previo."
    mensajes = [
        {"role": "system", "content": "Eres J.A.R.V.I.S., experto en observabilidad de datos. Responde en español de forma útil y concisa."},
        {"role": "user", "content": f"Fallo: {contexto}. Pregunta: {chat_req.pregunta}"}
    ]
    # CAMBIO FINAL: Nombres exactos actualizados
    for modelo in ["openai/gpt-oss-20b", "qwen/qwen3-32b"]:
        try:
            respuesta = client.chat.completions.create(messages=mensajes, model=modelo, temperature=0.3)
            if respuesta.choices[0].message.content: return {"respuesta": respuesta.choices[0].message.content}
        except Exception as e:
            print(f"Error IA en chat ({modelo}): {e}")
            continue
    return {"respuesta": "Analizando... verifique logs de la base de datos."}