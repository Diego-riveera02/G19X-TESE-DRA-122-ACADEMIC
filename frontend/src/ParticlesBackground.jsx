import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadSlim } from "tsparticles-slim";

const ParticlesBackground = () => {
  // Esta función inicializa el motor de partículas de forma ligera (slim)
  const particlesInit = useCallback(async (engine) => {
    await loadSlim(engine);
  }, []);

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        background: {
          color: {
            value: "#0b0c10", // El fondo oscuro de PluriOne
          },
        },
        fpsLimit: 60, // Límite de cuadros para no consumir mucha memoria
        interactivity: {
          events: {
            onHover: {
              enable: true,
              mode: "repulse", // Las partículas se alejan un poco del mouse
            },
            resize: true,
          },
          modes: {
            repulse: {
              distance: 100,
              duration: 0.4,
            },
          },
        },
        particles: {
          color: {
            value: ["#E5B80B", "#E63946", "#ffffff"], // Dorado, Rojo PluriOne y Blanco
          },
          links: {
            color: "#E5B80B",
            distance: 150,
            enable: true,
            opacity: 0.2,
            width: 1,
          },
          move: {
            direction: "none",
            enable: true,
            outModes: {
              default: "bounce",
            },
            random: true,
            speed: 1.2, // Movimiento elegante y lento
            straight: false,
          },
          number: {
            density: {
              enable: true,
              area: 800,
            },
            value: 80, // Número de partículas en pantalla
          },
          opacity: {
            value: 0.6,
          },
          shape: {
            type: "circle",
          },
          size: {
            value: { min: 1, max: 3 },
          },
        },
        detectRetina: true,
      }}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: -1, // Crucial: Esto asegura que el fondo quede detrás de los formularios
      }}
    />
  );
};

export default ParticlesBackground;