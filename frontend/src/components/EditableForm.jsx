import { useState, useEffect, useRef } from "react";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import "../styles/form.css";

export default function EditableForm({ data, serviceId }) {
  const [generating, setGenerating] = useState(false);
  // Track which field is currently being edited (null = none)
  const [editingField, setEditingField] = useState(null);
  const inputRef = useRef(null);

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

  // Auto-focus input when a field enters edit mode
  useEffect(() => {
    if (editingField && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editingField]);

  const handleChange = (field, value) => {
    setFormData((p) => ({ ...p, [field]: value }));
  };

  const handleEditClick = (field) => {
    setEditingField(field);
  };

  const handleSaveField = () => {
    setEditingField(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSaveField();
    }
    if (e.key === "Escape") {
      setEditingField(null);
    }
  };

  const today = new Date();
  const [formNumber] = useState(
    `SFAI-${today.getFullYear()}-${String(Math.floor(Math.random() * 99999)).padStart(5, "0")}`
  );
  const formDate = today.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  const handleDownloadPDF = async () => {
    const element = document.getElementById("govt-form-printable");
    if (!element) return;

    try {
      setGenerating(true);
      setEditingField(null); // Close any editing

      element.classList.add("pdf-capture");
      await new Promise((r) => setTimeout(r, 400));

      const canvas = await html2canvas(element, {
        scale: 2.5,
        useCORS: true,
        backgroundColor: "#ffffff",
        scrollY: 0,
        y: 0,
        windowWidth: 800,
        logging: false,
        onclone: (doc) => {
          const el = doc.getElementById("govt-form-printable");
          if (el) {
            el.style.padding = "32px";
            el.style.width = "800px";
            // Hide edit buttons and screen-only elements
            el.querySelectorAll(".mf-edit-btn, .mf-save-btn, .form-actions, .screen-only-element").forEach(
              (b) => (b.style.display = "none")
            );
            // Make all text black and inputs look like printed text
            el.querySelectorAll("input, select, textarea").forEach((inp) => {
              inp.style.color = "#000";
              inp.style.borderColor = "#999";
              inp.style.background = "transparent";
              inp.style.WebkitTextFillColor = "#000";
            });
            // Show values as plain text
            el.querySelectorAll(".mf-display-value").forEach((v) => {
              v.style.color = "#000";
            });
          }
        },
      });

      const imgData = canvas.toDataURL("image/jpeg", 0.95);
      const pdf = new jsPDF("p", "mm", "a4");
      const pageW = 210;
      const pageH = 297;
      const m = 6;
      const imgW = pageW - m * 2;
      const imgH = (canvas.height * imgW) / canvas.width;

      let hLeft = imgH;
      let pos = m;

      pdf.addImage(imgData, "JPEG", m, pos, imgW, imgH);
      hLeft -= pageH - m * 2;

      while (hLeft > 0) {
        pos = hLeft - imgH + m;
        pdf.addPage();
        pdf.addImage(imgData, "JPEG", m, pos, imgW, imgH);
        hLeft -= pageH - m * 2;
      }

      pdf.save(`${serviceName.replace(/\s+/g, "_")}_Application_${formNumber}.pdf`);
      element.classList.remove("pdf-capture");
      setGenerating(false);
    } catch (err) {
      element?.classList.remove("pdf-capture");
      setGenerating(false);
      console.error(err);
      alert("PDF generation failed. Please try again.");
    }
  };

  // ═══ Per-field component ═══
  const Field = ({ label, field, half, type = "text", placeholder = "", choices }) => {
    const isEditing = editingField === field;
    const value = formData[field] || "";
    const hasValue = value.length > 0;

    return (
      <div className={`mf-field ${half ? "mf-half" : ""}`}>
        <div className="mf-field-header">
          <label className="mf-label">{label}</label>
          {!isEditing ? (
            <button
              className="mf-edit-btn"
              onClick={() => handleEditClick(field)}
              title={`Edit ${label}`}
              type="button"
            >
              ✏️
            </button>
          ) : (
            <button
              className="mf-save-btn"
              onClick={handleSaveField}
              title="Save"
              type="button"
            >
              ✅
            </button>
          )}
        </div>

        {isEditing ? (
          // ── EDIT MODE ──
          type === "select" ? (
            <select
              ref={inputRef}
              className="mf-input mf-input-editing"
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              onBlur={handleSaveField}
            >
              <option value="">— Select —</option>
              {choices?.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          ) : (
            <input
              ref={inputRef}
              type={type}
              className="mf-input mf-input-editing"
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSaveField}
              placeholder={placeholder}
            />
          )
        ) : (
          // ── DISPLAY MODE ──
          <div
            className={`mf-display-value ${hasValue ? "" : "mf-empty"}`}
            onClick={() => handleEditClick(field)}
          >
            {hasValue ? value : placeholder || "—"}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="mf-wrapper">
      <div id="govt-form-printable" className="mf-container">

        {/* ═══ Header ═══ */}
        <div className="mf-header">
          <div className="mf-header-top">
            <div className="mf-emblem">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"
                alt="National Emblem of India"
                className="mf-emblem-img"
                crossOrigin="anonymous"
              />
            </div>
            <div className="mf-header-text">
              <h1 className="mf-header-title">Government of India</h1>
              <p className="mf-header-ministry">Ministry of Electronics & Information Technology</p>
              <p className="mf-header-portal">Seva Form AI — Digital Application Portal</p>
            </div>
          </div>
          <div className="mf-header-bar">
            <div className="mf-bar-item">
              <span className="mf-bar-label">Service</span>
              <span className="mf-bar-value">{serviceName}</span>
            </div>
            <div className="mf-bar-item">
              <span className="mf-bar-label">Application No.</span>
              <span className="mf-bar-value">{formNumber}</span>
            </div>
            <div className="mf-bar-item">
              <span className="mf-bar-label">Date</span>
              <span className="mf-bar-value">{formDate}</span>
            </div>
          </div>
        </div>

        {/* ═══ Screen banner ═══ */}
        <div className="screen-only-element mf-screen-banner">
          Click ✏️ on any field to edit it individually
        </div>

        {/* ═══ Section 1: Personal ═══ */}
        <div className="mf-section">
          <div className="mf-section-title">
            <span className="mf-section-num">01</span>
            Personal Information
          </div>
          <div className="mf-fields-grid">
            <Field label="Full Name" field="name" placeholder="As per Aadhaar card" />
            <Field label="Date of Birth" field="dob" half placeholder="DD/MM/YYYY" />
            <Field label="Gender" field="gender" half type="select" choices={["Male", "Female", "Other"]} />
            <Field label="Father's Name" field="father_name" />
            <Field label="Mother's Name" field="mother_name" />
            <Field label="Marital Status" field="marital_status" half type="select" choices={["Single", "Married", "Widowed", "Divorced"]} />
            <Field label="Caste / Category" field="caste" half placeholder="General, OBC, SC, ST" />
          </div>
        </div>

        {/* ═══ Section 2: Identity ═══ */}
        <div className="mf-section">
          <div className="mf-section-title">
            <span className="mf-section-num">02</span>
            Identity & Contact
          </div>
          <div className="mf-fields-grid">
            <Field label="Aadhaar Number" field="aadhaar" half placeholder="XXXX XXXX XXXX" />
            <Field label="PAN Number" field="pan" half placeholder="ABCDE1234F" />
            <Field label="Mobile Number" field="mobile" half type="tel" placeholder="+91 XXXXXXXXXX" />
            <Field label="Email Address" field="email" half type="email" placeholder="you@email.com" />
          </div>
        </div>

        {/* ═══ Section 3: Address ═══ */}
        <div className="mf-section">
          <div className="mf-section-title">
            <span className="mf-section-num">03</span>
            Address Details
          </div>
          <div className="mf-fields-grid">
            <Field label="Present Address" field="address" placeholder="House No., Street, Locality" />
            <Field label="Village / Town / City" field="village" half />
            <Field label="Taluka / Tehsil" field="taluka" half />
            <Field label="District" field="district" half />
            <Field label="State" field="state" half />
            <Field label="PIN Code" field="pincode" half placeholder="6-digit code" />
            <Field label="Permanent Address" field="permanent_address" placeholder="If different from present address" />
          </div>
        </div>

        {/* ═══ Section 4: Declaration ═══ */}
        <div className="mf-section mf-declaration">
          <div className="mf-section-title">
            <span className="mf-section-num">04</span>
            Declaration
          </div>
          <div className="mf-decl-body">
            <p>
              I hereby declare that all the information provided above is true, complete and correct to the best
              of my knowledge and belief. I understand that any false statement or suppression of material facts
              may render my application liable for rejection and legal action as per the provisions of applicable law.
            </p>
            <div className="mf-sig-row">
              <div className="mf-sig-item">
                <div className="mf-sig-line"></div>
                <span>Place</span>
              </div>
              <div className="mf-sig-item">
                <div className="mf-sig-line"></div>
                <span>Date</span>
              </div>
              <div className="mf-sig-item mf-sig-main">
                <div className="mf-sig-line"></div>
                <span>Signature of Applicant</span>
              </div>
            </div>
          </div>
        </div>

        {/* ═══ Footer ═══ */}
        <div className="mf-footer">
          <span>Ref: {formNumber}</span>
          <span>Digitally generated via Seva Form AI</span>
          <span>Page 1 of 1</span>
        </div>
      </div>

      {/* ═══ Actions ═══ */}
      <div className="form-actions">
        <button
          className="mf-btn mf-btn-primary"
          onClick={handleDownloadPDF}
          disabled={generating}
        >
          {generating ? "⏳ Generating PDF..." : "📥 Download Application PDF"}
        </button>
      </div>
    </div>
  );
}
