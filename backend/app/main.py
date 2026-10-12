from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from . import models, schemas
from .database import engine, get_db

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 

SECRET_KEY = os.getenv("SECRET_KEY", "plurione_super_secret_key_2026") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =================================================================
#                 GESTOR DE WEBSOCKETS
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
#                 FUNCIONES DE UTILIDAD Y SEGURIDAD
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

# CORREO CONSOLIDADO: Muestra los tres estados (Normal, Alerta, Crítico) y el diagnóstico de la IA
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
    for modelo in ["openai/gpt-oss-20b", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
        try:
            chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=modelo)
            contenido = chat_completion.choices[0].message.content
            if contenido: return contenido
        except Exception: continue
    return f"Revisar anomalía en {pipeline_name}."

class ChatRequest(BaseModel):
    anomaly_id: int
    pregunta: str
    contexto_anomalia: str

# =================================================================
#                 ENDPOINTS DE AUTENTICACIÓN
# =================================================================
@app.post("/registro/", response_model=schemas.UserResponse)
def registrar_usuario(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.correo == user.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    nuevo_usuario = models.User(nombre_completo=user.nombre_completo, correo=user.correo, telefono=user.telefono, hashed_password=get_password_hash(user.password))
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer", "nombre": user.nombre_completo, "correo": user.correo}

# =================================================================
#                 ENDPOINTS DE OBSERVABILIDAD
# =================================================================
@app.post("/anomalias/", response_model=schemas.AnomalyLogResponse)
async def create_anomaly(anomalia: schemas.AnomalyLogCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    recomendacion = generar_recomendacion_ia(anomalia.pipeline_name, anomalia.metric_type, anomalia.value)
    anomalia.ai_recommendation = recomendacion

    db_anomalia = models.AnomalyLog(**anomalia.model_dump())
    db.add(db_anomalia)
    db.commit()
    db.refresh(db_anomalia)

    # Al ocurrir un estado crítico, consolidamos los estados actuales de los tres componentes y generamos el diagnóstico IA global
    if anomalia.status == "Critico":
        lat = db.query(models.AnomalyLog).filter(models.AnomalyLog.metric_type == "latencia_ms").order_by(models.AnomalyLog.id.desc()).first()
        cal = db.query(models.AnomalyLog).filter(models.AnomalyLog.metric_type == "datos_corruptos_%").order_by(models.AnomalyLog.id.desc()).first()
        fal = db.query(models.AnomalyLog).filter(models.AnomalyLog.metric_type == "tasa_fallos_%").order_by(models.AnomalyLog.id.desc()).first()

        lat_v = f"{lat.value} ms" if lat else "0 ms"
        lat_s = lat.status if lat else "Normal"
        cal_v = f"{cal.value} %" if cal else "0 %"
        cal_s = cal.status if cal else "Normal"
        fal_v = f"{fal.value} %" if fal else "0 %"
        fal_s = fal.status if fal else "Normal"

        prompt_global = f"Estado actual de infraestructura:\n1. Latencia API Gateway: {lat_v} [Estado: {lat_s}]\n2. Calidad Ventas MX: {cal_v} [Estado: {cal_s}]\n3. Fallos AWS: {fal_v} [Estado: {fal_s}]\nAnaliza por qué se originó este fallo crítico y explica las causas técnicas de manera clara en un párrafo conciso."
        diag_general = "Se detectó una degradación crítica en los servicios que requiere revisión inmediata de los logs de red y base de datos."
        
        for modelo in ["openai/gpt-oss-20b", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_global}], model=modelo)
                if res.choices[0].message.content: 
                    diag_general = res.choices[0].message.content
                    break
            except Exception: continue

        background_tasks.add_task(enviar_alerta_correo_consolidado, current_user.correo, lat_v, lat_s, cal_v, cal_s, fal_v, fal_s, diag_general)

    mensaje_ws = json.dumps({
        "id": db_anomalia.id,
        "pipeline_name": db_anomalia.pipeline_name,
        "metric_type": db_anomalia.metric_type,
        "value": db_anomalia.value,
        "status": db_anomalia.status,
        "ai_recommendation": db_anomalia.ai_recommendation
    })
    await manager.broadcast(mensaje_ws)

    return db_anomalia

@app.get("/anomalias/", response_model=list[schemas.AnomalyLogResponse])
def read_anomalies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.AnomalyLog).offset(skip).limit(limit).all()

@app.delete("/anomalias/")
def clear_anomalies(db: Session = Depends(get_db)):
    db.query(models.AnomalyLog).delete()
    db.commit()
    return {"status": "Historial borrado exitosamente"}

@app.post("/chat/")
def chat_causa_raiz(chat_req: ChatRequest):
    contexto = chat_req.contexto_anomalia if chat_req.contexto_anomalia else "Sin diagnóstico previo."
    mensajes = [
        {"role": "system", "content": "Eres J.A.R.V.I.S., experto en datos. Responde en español."},
        {"role": "user", "content": f"Fallo: {contexto}. Pregunta: {chat_req.pregunta}"}
    ]
    for modelo in ["openai/gpt-oss-20b", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
        try:
            respuesta = client.chat.completions.create(messages=mensajes, model=modelo, temperature=0.3)
            if respuesta.choices[0].message.content: return {"respuesta": respuesta.choices[0].message.content}
        except Exception: continue
    return {"respuesta": "Analizando... verifique logs de la base de datos."}