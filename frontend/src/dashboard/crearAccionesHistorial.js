import { api } from '../api';

export function crearAccionesHistorial({
  procesandoHistorial,
  setProcesandoHistorial,
  nombreUsuario,
  setIdOcultosHasta,
  setAnomalias,
  setMetricasEnVivo,
  navigate
}) {
  const limpiarHistorial = async () => {
    if (procesandoHistorial) return;

    const confirmar = window.confirm(
      'Se archivaran TODAS las anomalias de tu cuenta, incluso las no visibles. Podras restaurarlas. Deseas continuar?'
    );
    if (!confirmar) return;

    if (!localStorage.getItem("token_plurione")) {
      navigate('/login');
      return;
    }

    setProcesandoHistorial(true);
    try {
      await api.delete("/anomalias/");

      localStorage.removeItem(`plurione_id_ocultos_${nombreUsuario}`);
      setIdOcultosHasta(0);
      setAnomalias([]);
      setMetricasEnVivo({});
      window.alert('Historial archivado. Puedes restaurarlo cuando quieras.');
    } catch {
      window.alert('No fue posible archivar el historial. Los datos visibles no se modificaron.');
    } finally {
      setProcesandoHistorial(false);
    }
  };

  const restaurarHistorial = async () => {
    if (procesandoHistorial) return;

    const confirmar = window.confirm(
      'Se restauraran las anomalias archivadas de tu cuenta. Deseas continuar?'
    );
    if (!confirmar) return;

    if (!localStorage.getItem("token_plurione")) {
      navigate('/login');
      return;
    }

    setProcesandoHistorial(true);
    try {
      await api.post("/anomalias/restaurar/", {});

      localStorage.removeItem(`plurione_id_ocultos_${nombreUsuario}`);
      setIdOcultosHasta(0);

      const respuesta = await api.get("/anomalias/");

      setAnomalias(
        respuesta.data.sort((a, b) => b.id - a.id)
      );
      setMetricasEnVivo({});
      window.alert('Historial restaurado correctamente.');
    } catch {
      window.alert('No se pudo completar la restauracion. Actualiza la pagina para consultar el estado actual.');
    } finally {
      setProcesandoHistorial(false);
    }
  };

  return { limpiarHistorial, restaurarHistorial };
}
