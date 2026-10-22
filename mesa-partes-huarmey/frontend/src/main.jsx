import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import './styles/variables.css';
import './styles/global.css';
import './styles/components.css';
import './styles/forms.css';
import './styles/cargo.css';
import './styles/admin.css';

// Punto de entrada: monta la aplicación React dentro de <div id="root">.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
