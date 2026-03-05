import { useState, useEffect } from "react";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import "../styles/form.css";

export default function EditableForm({ data, serviceId }) {
  const [previewMode, setPreviewMode] = useState(false);

  const serviceNames = {
    service_001: "Birth Certificate",
    service_002: "Caste Certificate",
    service_003: "Income Certificate",
    service_004: "Residence Certificate",
    service_005: "PM SVANidhi Yojana",
  };

  const serviceName = serviceNames[serviceId] || "General Application";

  const [formData, setFormData] = useState({
    name: "",
    dob: "",
    gender: "",
    father_name: "",
    mother_name: "",
    address: "",
    permanent_address: "",
    aadhaar: "",
    pan: "",
    mobile: "",
    email: "",
    caste: "",
    marital_status: "",
    pincode: "",
    district: "",
    state: "",
    village: "",
    taluka: "",
  });

  useEffect(() => {
    if (data) {
      setFormData((prev) => ({ ...prev, ...data }));
    }
  }, [data]);

  const handleChange = (field, value) => {
    setFormData((p) => ({ ...p, [field]: value }));
  };

  const today = new Date();
  const formNumber = `SFAI/${serviceId?.toUpperCase() || "GEN"}/${today.getFullYear()}/${String(Math.floor(Math.random() * 9999)).padStart(4, "0")}`;
  const formDate = today.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!previewMode) {
      setPreviewMode(true);
      return;
    }

    const element = document.querySelector(".editable-form-container");
    if (!element) return;

    try {
      const btn = e.target;
      const oldText = btn.textContent;
      btn.textContent = "⏳ Generating PDF...";
      btn.disabled = true;

      element.classList.add("pdf-mode");

      const style = document.createElement("style");
      style.innerHTML = `
        .pdf-mode button, .pdf-mode .form-submit-section,
        .pdf-mode .preview-actions, .pdf-mode nav,
        .pdf-mode header, .pdf-mode .screen-only {
          display: none !important;
        }
        .pdf-mode ::placeholder {
          color: transparent !important;
          opacity: 0 !important;
        }
      `;
      document.head.appendChild(style);

      await new Promise((resolve) => setTimeout(resolve, 500));

      const canvas = await html2canvas(element, {
        scale: 3,
        useCORS: true,
        backgroundColor: "#ffffff",
        scrollY: -window.scrollY,
        windowWidth: 850,
        logging: false,
      });

      const imgData = canvas.toDataURL("image/jpeg", 1.0);

      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = 210;
      const pageHeight = 297;
      const margin = 8;

      const imgWidth = pageWidth - margin * 2;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = margin;

      pdf.addImage(imgData, "JPEG", margin, position, imgWidth, imgHeight);
      heightLeft -= pageHeight - margin * 2;

      while (heightLeft > 0) {
        position = heightLeft - imgHeight + margin;
        pdf.addPage();
        pdf.addImage(imgData, "JPEG", margin, position, imgWidth, imgHeight);
        heightLeft -= pageHeight - margin * 2;
      }

      pdf.save(`GOI_${serviceName.replace(/\s+/g, "_")}_${Date.now()}.pdf`);

      element.classList.remove("pdf-mode");
      document.head.removeChild(style);
      btn.textContent = oldText;
      btn.disabled = false;
    } catch (err) {
      element.classList.remove("pdf-mode");
      console.error(err);
      alert("PDF generation failed");
    }
  };

  const renderField = (label, key, options = {}) => {
    const { type = "text", half = false, placeholder = "" } = options;

    if (type === "select") {
      return (
        <div className={`govt-field ${half ? "half" : ""}`} key={key}>
          <label className="govt-field-label">{label}</label>
          <select
            className="govt-field-input"
            value={formData[key] || ""}
            onChange={(e) => handleChange(key, e.target.value)}
            disabled={previewMode}
          >
            <option value="">— Select —</option>
            {options.choices?.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      );
    }

    return (
      <div className={`govt-field ${half ? "half" : ""}`} key={key}>
        <label className="govt-field-label">{label}</label>
        <input
          type={type}
          className="govt-field-input"
          value={formData[key] || ""}
          onChange={(e) => handleChange(key, e.target.value)}
          readOnly={previewMode}
          placeholder={placeholder}
        />
      </div>
    );
  };

  return (
    <div className="editable-form-container">
      <div className={`govt-form ${previewMode ? "preview-mode" : ""}`}>

        {/* ═══════════ OFFICIAL HEADER ═══════════ */}
        <div className="govt-form-header">
          <div className="govt-emblem">
            {/* Ashoka Lion Capital — text emblem for PDF compatibility */}
            <div className="emblem-icon">🏛️</div>
            <div className="emblem-text-block">
              <div className="emblem-hindi">भारत सरकार</div>
              <div className="emblem-title">GOVERNMENT OF INDIA</div>
              <div className="emblem-dept">MINISTRY OF ELECTRONICS & INFORMATION TECHNOLOGY</div>
              <div className="emblem-subtitle">SEVA FORM AI — e-Application Portal</div>
            </div>
          </div>

          <div className="form-meta-strip">
            <div className="form-meta-item">
              <span className="meta-label">FORM TYPE</span>
              <span className="meta-value">{serviceName}</span>
            </div>
            <div className="form-meta-item">
              <span className="meta-label">APPLICATION NO.</span>
              <span className="meta-value">{formNumber}</span>
            </div>
            <div className="form-meta-item">
              <span className="meta-label">DATE</span>
              <span className="meta-value">{formDate}</span>
            </div>
          </div>
        </div>

        {/* screen-only title */}
        <h3 className="screen-only form-mode-title">
          {previewMode ? "📋 Review & Download Application" : "✏️ Auto-Filled Application — Edit if needed"}
        </h3>

        {/* ═══════════ SECTION 1: Personal Details ═══════════ */}
        <div className="govt-section">
          <div className="govt-section-header">
            <span className="section-number">1</span>
            <span className="section-title">PERSONAL DETAILS / व्यक्तिगत विवरण</span>
          </div>
          <div className="govt-field-grid">
            {renderField("Full Name (पूरा नाम)", "name", { placeholder: "As per Aadhaar" })}
            {renderField("Date of Birth (जन्म तिथि)", "dob", { half: true, type: "text", placeholder: "DD/MM/YYYY" })}
            {renderField("Gender (लिंग)", "gender", { half: true, type: "select", choices: ["Male", "Female", "Other"] })}
            {renderField("Father's Name (पिता का नाम)", "father_name")}
            {renderField("Mother's Name (माता का नाम)", "mother_name")}
            {renderField("Marital Status (वैवाहिक स्थिति)", "marital_status", { half: true, type: "select", choices: ["Single", "Married", "Widowed", "Divorced"] })}
            {renderField("Caste / Category (जाति / श्रेणी)", "caste", { half: true, placeholder: "SC / ST / OBC / General" })}
          </div>
        </div>

        {/* ═══════════ SECTION 2: Identity Documents ═══════════ */}
        <div className="govt-section">
          <div className="govt-section-header">
            <span className="section-number">2</span>
            <span className="section-title">IDENTITY DOCUMENTS / पहचान दस्तावेज</span>
          </div>
          <div className="govt-field-grid">
            {renderField("Aadhaar Number (आधार संख्या)", "aadhaar", { half: true, placeholder: "XXXX XXXX XXXX" })}
            {renderField("PAN Number (पैन संख्या)", "pan", { half: true, placeholder: "XXXXX0000X" })}
            {renderField("Mobile Number (मोबाइल नंबर)", "mobile", { half: true, type: "tel", placeholder: "+91 XXXXXXXXXX" })}
            {renderField("Email (ईमेल)", "email", { half: true, type: "email", placeholder: "example@mail.com" })}
          </div>
        </div>

        {/* ═══════════ SECTION 3: Address Details ═══════════ */}
        <div className="govt-section">
          <div className="govt-section-header">
            <span className="section-number">3</span>
            <span className="section-title">ADDRESS DETAILS / पता विवरण</span>
          </div>
          <div className="govt-field-grid">
            {renderField("Present Address (वर्तमान पता)", "address", { placeholder: "House No., Street, Locality" })}
            {renderField("Village / Town / City (गाँव / नगर)", "village", { half: true })}
            {renderField("Taluka / Tehsil (तालुका / तहसील)", "taluka", { half: true })}
            {renderField("District (जिला)", "district", { half: true })}
            {renderField("State (राज्य)", "state", { half: true })}
            {renderField("PIN Code (पिन कोड)", "pincode", { half: true, placeholder: "6-digit PIN" })}
            {renderField("Permanent Address (स्थायी पता)", "permanent_address", { placeholder: "Same as above if applicable" })}
          </div>
        </div>

        {/* ═══════════ SECTION 4: Declaration ═══════════ */}
        <div className="govt-section declaration-section">
          <div className="govt-section-header">
            <span className="section-number">4</span>
            <span className="section-title">DECLARATION / घोषणा</span>
          </div>
          <div className="declaration-content">
            <p>
              I hereby declare that all the information furnished above is true, complete, and correct
              to the best of my knowledge and belief. I understand that in the event of any information
              being found false or incorrect, my application shall be liable for rejection and appropriate
              action may be initiated against me as per the provisions of law.
            </p>
            <p className="declaration-hindi">
              मैं एतद्द्वारा घोषणा करता/करती हूँ कि ऊपर दी गई समस्त जानकारी मेरी जानकारी और विश्वास
              के अनुसार सत्य, पूर्ण और सही है।
            </p>
            <div className="signature-block">
              <div className="sig-item">
                <div className="sig-line"></div>
                <span>Place / स्थान</span>
              </div>
              <div className="sig-item">
                <div className="sig-line"></div>
                <span>Date / दिनांक</span>
              </div>
              <div className="sig-item">
                <div className="sig-line"></div>
                <span>Signature of Applicant / आवेदक के हस्ताक्षर</span>
              </div>
            </div>
          </div>
        </div>

        {/* ═══════════ FORM FOOTER ═══════════ */}
        <div className="govt-form-footer">
          <div className="footer-left">
            <span>Ref: {formNumber}</span>
          </div>
          <div className="footer-center">
            <span>This is a computer-generated document from the Seva Form AI Portal</span>
          </div>
          <div className="footer-right">
            <span>Page 1 of 1</span>
          </div>
        </div>

        {/* ═══════════ ACTIONS ═══════════ */}
        <div className="form-submit-section">
          {!previewMode ? (
            <button className="btn-submit-form" onClick={handleSubmit}>
              📋 Preview Application
            </button>
          ) : (
            <div className="preview-actions">
              <button className="btn-edit" onClick={() => setPreviewMode(false)}>
                ✏️ Edit Form
              </button>
              <button className="btn-confirm" onClick={handleSubmit}>
                📥 Download PDF
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
