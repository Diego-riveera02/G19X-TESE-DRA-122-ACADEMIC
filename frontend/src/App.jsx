import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './Login';
import Registro from './Registro';
import Verificar from './Verificar';
import RecuperarPassword from './RecuperarPassword';
import Dashboard from './Dashboard';
import Pipelines from './Pipelines';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/verificar" element={<Verificar />} />
        <Route path="/recuperar" element={<RecuperarPassword />} />
        <Route path="/app" element={<Dashboard />} />
        <Route path="/pipelines" element={<Pipelines />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}
