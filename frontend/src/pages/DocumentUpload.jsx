import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { uploadDocument, getService, generateFormFromDocuments } from "../api/backend";
import Header from "../components/Header";
import EditableForm from "../components/EditableForm";
import "../styles/DocumentUpload.css";

export default function DocumentUpload() {
  const { serviceId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({});
  const [loadingDoc, setLoadingDoc] = useState("");
  const [documentResults, setDocumentResults] = useState({});
  const [filledForm, setFilledForm] = useState(null);
  const [processingForm, setProcessingForm] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
   
    setLoading(true);
    getService(serviceId)
      .then((data) => {
        setService(data);
       
        const initialStatus = {};
        if (data.required_documents) {
          data.required_documents.forEach((doc) => {
            const key = doc.name.toLowerCase().replace(/\s+/g, "_");
            initialStatus[key] = "";
          });
        }
        setStatus(initialStatus);
      })
      .catch((err) => {
        console.error("Failed to load service:", err);
      })
      .finally(() => setLoading(false));
  }, [serviceId]);

  
  useEffect(() => {
    if (!service || showForm || processingForm) return;

    const canProceed = service.required_documents
      ? service.required_documents
        .filter((doc) => doc.mandatory)
        .every((doc) => {
          const key = doc.name.toLowerCase().replace(/\s+/g, "_");
          return status[key] === "done";
        })
      : false;

  
    const hasAllResults = service.required_documents
      ? service.required_documents
        .filter((doc) => doc.mandatory)
        .every((doc) => {
          const key = doc.name.toLowerCase().replace(/\s+/g, "_");
          return documentResults[key] && documentResults[key].status === "success";
        })
      : false;

    if (canProceed && hasAllResults) {
      autoGenerateForm();
    }
  }, [status, service, documentResults, showForm, processingForm]);

  const handleUpload = async (documentName, file) => {
    if (!file) return;

    setLoadingDoc(documentName);
    setStatus((prev) => ({ ...prev, [documentName]: "uploading" }));

    try {
      const result = await uploadDocument({
        service_id: serviceId,
        document_name: documentName,
        file,
      });

      setDocumentResults((prev) => ({
        ...prev,
        [documentName]: result.ai_result,
      }));

      setStatus((prev) => ({ ...prev, [documentName]: "done" }));
    } catch (error) {
      console.error(error);
      setStatus((prev) => ({ ...prev, [documentName]: "error" }));
    } finally {
      setLoadingDoc("");
    }
  };

  const autoGenerateForm = async () => {
    setProcessingForm(true);
    try {
      const entitiesList = Object.values(documentResults).filter(
        (result) => result && result.status === "success"
      );

      if (entitiesList.length > 0) {
        const formResult = await generateFormFromDocuments(serviceId, entitiesList);
        if (formResult.status === "success") {
          setFilledForm(formResult.filled_form);
          setShowForm(true);
        }
      }
    } catch (error) {
      console.error("Failed to generate form:", error);
    } finally {
      setProcessingForm(false);
    }
  };

  const canProceed = service?.required_documents
    ? service.required_documents
      .filter((doc) => doc.mandatory)
      .every((doc) => {
        const key = doc.name.toLowerCase().replace(/\s+/g, "_");
        return status[key] === "done";
      })
    : false;

  if (loading) {
    return (
      <>
        <Header />
        <div className="upload-container">
          <p>Loading service details...</p>
        </div>
      </>
    );
  }

  if (!service) {
    return (
      <>
        <Header />
        <div className="upload-container">
          <p>Service not found. Please go back and select a service.</p>
          <button onClick={() => navigate("/services")}>Go Back</button>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="upload-container">
        <div className="service-header-section">
          <h2>Upload Required Documents</h2>
          <div className="service-info">
            <h3>{t(service.service_name)}</h3>
            <p className="category-tag">{t(service.category)}</p>
          </div>
        </div>

        <p className="instruction-text">
          Upload the required documents below. Our AI will automatically extract information
          from your documents (Aadhaar, PAN, Voter ID, etc.) to auto-fill the form.
        </p>

        {service.required_documents && service.required_documents.length > 0 ? (
          <div className="documents-list">
            {service.required_documents.map((doc, idx) => {
              const docKey = doc.name.toLowerCase().replace(/\s+/g, "_");
              const isUploading = loadingDoc === docKey;
              const uploadStatus = status[docKey] || "";

              return (
                <div className="upload-card" key={idx}>
                  <div className="upload-card-header">
                    <label>
                      {t(doc.name)} {doc.mandatory && <span className="required-star">*</span>}
                    </label>
                    {!doc.mandatory && <span className="optional-badge">Optional</span>}
                  </div>
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    disabled={isUploading}
                    onChange={(e) => handleUpload(docKey, e.target.files[0])}
                  />
                  <span className={`status ${uploadStatus}`}>
                    {uploadStatus === "uploading" && "⏳ Processing..."}
                    {uploadStatus === "done" && "✅ Uploaded & Processed"}
                    {uploadStatus === "error" && "❌ Upload Failed"}
                    {!uploadStatus && "📄 No file selected"}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <p>No documents required for this service.</p>
        )}

        <p className="hint">
          📄 Supported formats: JPG, PNG, PDF • 🤖 AI automatically extracts details from your documents
        </p>

        {processingForm && (
          <div className="form-processing">
            <div className="processing-spinner"></div>
            <p>🤖 AI is processing your documents and auto-filling the form...</p>
          </div>
        )}

        {showForm && filledForm && (
          <div className="auto-filled-form-section">
            <div className="form-section-header">
              <h3>✅ Form Auto-Filled from Documents</h3>
              <p className="form-subtitle">
                Review and edit the information extracted from your documents. You can also use voice to fill or adjust any fields.
              </p>
            </div>

            <EditableForm data={filledForm} serviceId={serviceId} />

            <div className="form-actions">
              <button
                className="btn-voice-optional"
                onClick={() => navigate(`/voice/${serviceId}`, { state: { existingForm: filledForm } })}
              >
                🎤 Use Voice to Fill/Adjust
              </button>
            </div>
          </div>
        )}

        {!showForm && canProceed && !processingForm && (
          <button
            className="next-btn"
            onClick={autoGenerateForm}
          >
            🤖 Generate Form from Documents
          </button>
        )}





        {!canProceed && (
          <p className="upload-reminder">
            Please upload all required documents marked with *
          </p>
        )}

        <button
          className="back-btn"
          onClick={() => navigate("/services")}
          style={{ marginTop: "10px" }}
        >
          ← Back to Services
        </button>
      </div>
    </>
  );
}
