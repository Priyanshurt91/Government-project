import { useState, useEffect } from "react";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import "../styles/form.css";

export default function EditableForm({ data, serviceId }) {
  const [previewMode, setPreviewMode] = useState(false);
  const [generating, setGenerating] = useState(false);

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
  const formNumber = `SFAI-${today.getFullYear()}-${String(Math.floor(Math.random() * 99999)).padStart(5, "0")}`;
  const formDate = today.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!previewMode) {
      setPreviewMode(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const element = document.getElementById("govt-form-printable");
    if (!element) return;

    try {
      setGenerating(true);

      // Add PDF class for clean rendering
      element.classList.add("pdf-capture");

      // Wait for styles to apply
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
            // Hide buttons in clone
            const btns = el.querySelectorAll(".form-actions, .screen-only-element");
            btns.forEach((b) => (b.style.display = "none"));
            // Make all text black
            el.querySelectorAll("input, select, textarea").forEach((inp) => {
              inp.style.color = "#000";
              inp.style.borderColor = "#999";
              inp.style.background = "transparent";
              inp.style.WebkitTextFillColor = "#000";
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

  const Field = ({ label, field, half, type = "text", placeholder = "", choices }) => {
    if (type === "select") {
      return (
        <div className={`mf-field ${half ? "mf-half" : ""}`}>
          <label className="mf-label">{label}</label>
          <select
            className="mf-input"
            value={formData[field] || ""}
            onChange={(e) => handleChange(field, e.target.value)}
            disabled={previewMode}
          >
            <option value="">Select</option>
            {choices?.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      );
    }
    return (
      <div className={`mf-field ${half ? "mf-half" : ""}`}>
        <label className="mf-label">{label}</label>
        <input
          type={type}
          className="mf-input"
          value={formData[field] || ""}
          onChange={(e) => handleChange(field, e.target.value)}
          readOnly={previewMode}
          placeholder={placeholder}
        />
      </div>
    );
  };

  return (
    <div className="mf-wrapper">
      <div id="govt-form-printable" className={`mf-container ${previewMode ? "mf-preview" : ""}`}>

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

        {/* ═══ Screen title ═══ */}
        <div className="screen-only-element mf-screen-banner">
          {previewMode ? "📋 Review your details — then download PDF" : "✏️ Edit any auto-filled fields below"}
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

      {/* ═══ Actions (outside printable area) ═══ */}
      <div className="form-actions">
        {!previewMode ? (
          <button className="mf-btn mf-btn-primary" onClick={handleSubmit}>
            Preview Application →
          </button>
        ) : (
          <div className="mf-btn-group">
            <button className="mf-btn mf-btn-secondary" onClick={() => setPreviewMode(false)}>
              ← Edit Form
            </button>
            <button
              className="mf-btn mf-btn-primary"
              onClick={handleSubmit}
              disabled={generating}
            >
              {generating ? "Generating PDF..." : "📥 Download PDF"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
