import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import ServiceSelector from "./pages/ServiceSelector";
import DocumentUploadPage from "./pages/DocumentUpload";
import VoiceForm from "./pages/VoiceForm";
import AdminDashboard from "./pages/AdminDashboard";
import Blog from "./pages/Blog";
import About from "./pages/About";
import Contact from "./pages/Contact";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import FormPage from "./pages/FormPage";
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/services" element={<ServiceSelector />} />
      <Route path="/upload/:serviceId" element={<DocumentUploadPage />} />
      <Route path="/form/:serviceId" element={<FormPage />} />
      <Route path="/voice" element={<VoiceForm />} />
      <Route path="/voice/:serviceId" element={<VoiceForm />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/blog" element={<Blog />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/chat" element={<Chat />} />
    </Routes>
  );
}
