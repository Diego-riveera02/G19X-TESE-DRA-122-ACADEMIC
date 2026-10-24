import axios from "axios";

const configuredUrl = import.meta.env.VITE_API_URL?.trim();

export const API_URL = (
  configuredUrl || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export const WS_URL = API_URL.replace(/^http/, "ws");

export const api = axios.create({
  baseURL: API_URL,
});

// Las rutas de identidad funcionan sin JWT. Un error 401 en /login/
// no debe cerrar otra sesion ni redirigir antes de mostrar el mensaje.
const RUTAS_PUBLICAS = new Set([
  "/registro/",
  "/verificar/",
  "/reenviar-verificacion/",
  "/solicitar-recuperacion/",
  "/recuperar-password/",
  "/login/",
]);

const origenAPI = new URL(API_URL).origin;

function obtenerRuta(url) {
  return new URL(url || "", `${API_URL}/`);
}

function esSolicitudProtegida(config) {
  const destino = obtenerRuta(config?.url);
  return destino.origin === origenAPI && !RUTAS_PUBLICAS.has(destino.pathname);
}

export function limpiarSesion() {
  localStorage.removeItem("token_plurione");
  localStorage.removeItem("usuario_nombre");
}

api.interceptors.request.use((config) => {
  if (esSolicitudProtegida(config)) {
    const token = localStorage.getItem("token_plurione");
    if (token) {
      if (typeof config.headers?.set === "function") {
        config.headers.set("Authorization", `Bearer ${token}`);
      } else {
        config.headers = { ...config.headers, Authorization: `Bearer ${token}` };
      }
    }
  }
  return config;
});

let redireccionEnCurso = false;

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && esSolicitudProtegida(error.config)) {
      const autorizacion = error.config?.headers?.get?.("Authorization")
        || error.config?.headers?.Authorization;
      const tokenRechazado = autorizacion?.startsWith("Bearer ")
        ? autorizacion.slice(7)
        : null;

      // Una solicitud antigua no debe cerrar una sesion iniciada despues.
      if (tokenRechazado && localStorage.getItem("token_plurione") === tokenRechazado) {
        limpiarSesion();
        if (!redireccionEnCurso && window.location.pathname !== "/login") {
          redireccionEnCurso = true;
          window.location.replace("/login");
        }
      }
    }
    return Promise.reject(error);
  }
);
