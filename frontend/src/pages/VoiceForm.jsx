import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import MicRecorder from "../components/MicRecorder";
import EditableForm from "../components/EditableForm";
import { uploadVoice } from "../api/backend";
import Header from "../components/Header";
import "../styles/VoiceForm.css";

export default function VoiceForm() {
  const { t } = useTranslation();
  const { serviceId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [audioBlob, setAudioBlob] = useState(null);
  const [result, setResult] = useState(location.state?.existingForm ? { filled_form: location.state.existingForm } : null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const sendAudio = async () => {
    if (!audioBlob) return;

    setProcessing(true);
    setError(null);

    try {
      const file = new File([audioBlob], "voice.webm");
      const res = await uploadVoice(file, "transcribe");

      const currentForm = result?.filled_form || {};
      const newForm = res.filled_form || {};

      const mergedForm = { ...currentForm };

      Object.keys(newForm).forEach(key => {
        if (key === 'fields' && typeof newForm[key] === 'object') {
          mergedForm.fields = { ...(currentForm.fields || {}) };
          const newFields = newForm.fields || {};

          Object.keys(newFields).forEach(fieldKey => {
            if (newFields[fieldKey] && String(newFields[fieldKey]).trim() !== "") {
              mergedForm.fields[fieldKey] = newFields[fieldKey];
            }
          });
        } else if (newForm[key] && String(newForm[key]).trim() !== "") {
          mergedForm[key] = newForm[key];
        }
      });

      setResult({ ...res, filled_form: mergedForm });
    } catch (err) {
      setError(err.message || "Failed to process voice. Please try again.");
      console.error("Voice processing error:", err);
    } finally {
      setProcessing(false);
    }
  };

  const resetRecording = () => {
    setAudioBlob(null);
    setResult(null);
    setError(null);
  };

  return (
    <>
      <Header />
      <div className="voice-form-container">
        <div className="voice-form-content">
          <div className="voice-header">
            <div className="voice-icon">🎤</div>
            <h1>{t('voice_form.title')}</h1>
            <p className="voice-subtitle">
              {t('voice_form.subtitle')}
            </p>
          </div>

          <div className="recorder-section">
            <MicRecorder onRecorded={setAudioBlob} />

            {audioBlob && !result && (
              <div className="audio-actions">
                <p className="audio-status">✅ {t('voice_form.recording_completed')}</p>
                <div className="action-buttons">
                  <button
                    className="btn-process"
                    onClick={sendAudio}
                    disabled={processing}
                  >
                    {processing ? `⏳ ${t('voice_form.processing')}` : `📤 ${t('voice_form.process_voice')}`}
                  </button>
                  <button
                    className="btn-reset"
                    onClick={resetRecording}
                    disabled={processing}
                  >
                    🔄 {t('voice_form.record_again')}
                  </button>
                </div>
              </div>
            )}

            {processing && (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <p>{t('voice_form.processing')}</p>
              </div>
            )}

            {error && (
              <div className="error-message">
                <p>❌ {error}</p>
                <button onClick={resetRecording} className="btn-retry">
                  {t('voice_form.try_again')}
                </button>
              </div>
            )}
          </div>

          {result && (
            <div className="form-result">
              <div className="result-header">
                <h2>✅ {t('voice_form.success_title')}</h2>
                <button onClick={resetRecording} className="btn-new-recording">
                  🎤 {t('voice_form.new_recording')}
                </button>
              </div>
              <EditableForm data={result.filled_form?.fields || result.filled_form} />
            </div>
          )}

          {!serviceId && (
            <div className="navigation-options">
              <button onClick={() => navigate("/services")} className="btn-browse-services">
                📋 {t('voice_form.browse_services')}
              </button>
              <button onClick={() => navigate("/")} className="btn-back-home">
                ← {t('voice_form.back_home')}
              </button>
            </div>
          )}

          {serviceId && (
            <div className="navigation-options">
              <button onClick={() => navigate(`/upload/${serviceId}`)} className="btn-back-upload">
                ← {t('voice_form.back_upload')}
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
