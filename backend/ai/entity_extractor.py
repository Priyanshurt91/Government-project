import re


def _clean_space(s):
    """Normalize whitespace in a string."""
    return re.sub(r'\s+', ' ', s).strip()


def _parse_address_components(address_text):
    """
    Parse an Indian address string into components:
    village/city, taluka, district, state, pincode
    """
    components = {}
    
    # Extract pincode (6-digit number)
    pin_match = re.search(r'\b(\d{6})\b', address_text)
    if pin_match:
        components["pincode"] = pin_match.group(1)
    
    # Common Indian states
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry",
        "Andaman and Nicobar", "Dadra and Nagar Haveli", "Daman and Diu", "Lakshadweep"
    ]
    
    for state in states:
        if re.search(re.escape(state), address_text, re.IGNORECASE):
            components["state"] = state
            break
    
    # Try to extract district — look for "dist" or "district" label
    dist_match = re.search(r'(?:dist(?:rict)?)[.:\s]+([A-Za-z\s]+?)(?:,|\d{6}|$)', address_text, re.IGNORECASE)
    if dist_match:
        components["district"] = _clean_space(dist_match.group(1))
    
    # Extract village/city — first meaningful part of address
    parts = re.split(r'[,\n]', address_text)
    if parts:
        first_part = _clean_space(parts[0])
        # Remove common prefixes
        first_part = re.sub(r'^(?:S/O|D/O|W/O|C/O|H/No|House No)[.:\s]*[^,]*,?\s*', '', first_part, flags=re.IGNORECASE)
        if first_part and len(first_part) > 2:
            components["village"] = first_part
    
    return components


def extract_entities_aadhaar(text: str):
    """
    Entity extraction specifically optimized for Aadhaar cards.
    Handles Aadhaar-specific layouts:
    - Name appears before DOB/YOB line
    - S/O, D/O, W/O patterns for father/husband name
    - Year of Birth instead of full DOB
    - Address with pincode at the end
    """
    entities = {}
    text_clean = text.strip()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # === Aadhaar Number ===
    aadhaar_match = re.search(r'\b(\d{4}[\s\-]*\d{4}[\s\-]*\d{4})\b', text_clean)
    if aadhaar_match:
        entities["aadhaar"] = aadhaar_match.group(1).replace(" ", "").replace("-", "")
    
    # === DOB (full date format) ===
    dob_match = re.search(r'(?:DOB|Date of Birth|D\.O\.B|DOB\s*:)\s*[:/]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})', text_clean, re.IGNORECASE)
    if dob_match:
        entities["dob"] = dob_match.group(1)
    
    # === Year of Birth (Aadhaar-specific — many cards show only year) ===
    if "dob" not in entities:
        yob_match = re.search(r'(?:Year\s*of\s*Birth|YOB|Year\s*:)\s*[:/]?\s*(\d{4})', text_clean, re.IGNORECASE)
        if yob_match:
            entities["dob"] = yob_match.group(1)  # Store just the year
    
    # === Standalone date (Aadhaar cards often show date without label) ===
    if "dob" not in entities:
        for line in lines:
            line_stripped = re.sub(r'[^0-9/\-.]', '', line.strip())
            date_match = re.match(r'^(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})$', line_stripped)
            if date_match:
                entities["dob"] = date_match.group(1)
                break
        # Also try to find a date anywhere in the text as last resort
        if "dob" not in entities:
            any_date = re.search(r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})\b', text_clean)
            if any_date:
                entities["dob"] = any_date.group(1)
    
    # === Gender ===
    gender_match = re.search(r'\b(Male|Female|Transgender|MALE|FEMALE|पुरुष|महिला)\b', text_clean, re.IGNORECASE)
    if gender_match:
        val = gender_match.group(0)
        if val in ('पुरुष',):
            val = 'Male'
        elif val in ('महिला',):
            val = 'Female'
        else:
            val = val.capitalize()
        entities["gender"] = val
    
    # === Father/Husband Name ===
    # Pattern 1: S/O, D/O, W/O, C/O (common in older Aadhaar cards)
    relation_match = re.search(
        r'(?:S\s*/\s*O|D\s*/\s*O|W\s*/\s*O|C\s*/\s*O|s/o|d/o|w/o|c/o)[.:\s]+([A-Za-z\s.]+?)(?:\n|,|$)',
        text_clean, re.IGNORECASE
    )
    if relation_match:
        father_name = _clean_space(relation_match.group(1))
        father_name = re.sub(r'\b(Male|Female|DOB|Date|Year|Address)\b.*', '', father_name, flags=re.IGNORECASE).strip()
        if father_name and len(father_name) > 2:
            entities["father_name"] = father_name
    
    # Pattern 2: "Father :", "Father Name", "पिता :", "Husband :" (common in new Aadhaar cards)
    if "father_name" not in entities:
        father_label_match = re.search(
            r'(?:Father(?:\s*(?:\'s)?\s*(?:Name)?)?|पिता|Husband)\s*[:/]?\s+([A-Za-z\s.]+?)(?:\n|,|जन्म|DOB|Male|Female|पुरुष|महिला|$)',
            text_clean, re.IGNORECASE
        )
        if father_label_match:
            father_name = _clean_space(father_label_match.group(1))
            father_name = re.sub(r'\b(Male|Female|DOB|Date|Year|Address|Birth)\b.*', '', father_name, flags=re.IGNORECASE).strip()
            if father_name and len(father_name) > 2:
                entities["father_name"] = father_name
    
    # === Name Detection (Aadhaar-specific) ===
    # Strategy: The person's name on an Aadhaar card typically appears:
    # 1. On a line by itself, above the DOB/YOB line
    # 2. After "Government of India" header lines
    # 3. In English, as a proper capitalized name
    
    # Find the line index of DOB/YOB/Gender to know where name should be
    dob_line_idx = -1
    for i, line in enumerate(lines):
        if re.search(r'(DOB|Date of Birth|Year of Birth|YOB|\b\d{2}/\d{2}/\d{4}\b)', line, re.IGNORECASE):
            dob_line_idx = i
            break
    
    # Also find where S/O, D/O appears
    relation_line_idx = -1
    for i, line in enumerate(lines):
        if re.search(r'(S\s*/\s*O|D\s*/\s*O|W\s*/\s*O|C\s*/\s*O)', line, re.IGNORECASE):
            relation_line_idx = i
            break
    
    # Blacklist words that are NOT names
    name_blacklist = {
        'GOVERNMENT', 'INDIA', 'UIDAI', 'UNIQUE', 'IDENTIFICATION', 'AUTHORITY',
        'AADHAAR', 'AADHAR', 'ENROLMENT', 'ENROLLMENT', 'MALE', 'FEMALE',
        'ADDRESS', 'DOB', 'DATE', 'BIRTH', 'YEAR', 'VID', 'HELP',
        'YOUR', 'MOBILE', 'DOWNLOAD', 'MAADHAAR', 'WWW', 'UIDAI', 'GOV',
        'ISSUED', 'CARD', 'NUMBER', 'DEPARTMENT', 'TAX', 'INCOME',
        'FATHER', 'MOTHER', 'HUSBAND', 'WIFE', 'SON', 'DAUGHTER',
    }
    
    def is_valid_name(text_val):
        """Check if text looks like a person's name."""
        words = text_val.split()
        if len(words) < 2 or len(words) > 5:
            return False
        if len(text_val) < 4:
            return False
        # Each word should be at least 2 chars and alphabetic
        if not all(re.match(r'^[A-Za-z.]+$', w) and len(w) >= 2 for w in words):
            return False
        # No blacklisted words
        if any(w.upper() in name_blacklist for w in words):
            return False
        return True
    
    def name_score(text_val):
        """Score a name candidate — prefer ALL CAPS names (Aadhaar format)."""
        score = 0
        words = text_val.split()
        # ALL CAPS bonus (like MERAJ KHAN)
        if text_val == text_val.upper():
            score += 10
        # Title case bonus (like John Smith)
        elif all(w[0].isupper() for w in words):
            score += 5
        # Longer names are slightly preferred
        score += len(text_val) / 10
        return score
    
    # Header patterns to skip (not names)
    header_patterns = re.compile(
        r'(Government|UIDAI|Unique\s*Identification|Authority|Enrol|'
        r'भारत\s*सरकार|आधार|सत्यमेव|Satyamev)', re.IGNORECASE
    )
    
    if "name" not in entities:
        # Collect ALL valid name candidates with scores
        name_candidates = []
        search_end = dob_line_idx if dob_line_idx > 0 else len(lines)
        
        for i in range(0, search_end):
            line = lines[i].strip()
            # Skip header lines
            if header_patterns.search(line):
                continue
            # Skip relation/father lines
            if re.search(r'(S\s*/\s*O|D\s*/\s*O|W\s*/\s*O|C\s*/\s*O|Father|Husband|पिता)', line, re.IGNORECASE):
                continue
            if re.search(r'\d{4}\s*\d{4}\s*\d{4}', line):
                continue
            
            # Remove leading junk/labels
            name_candidate = re.sub(r'^(?:Name|To)\s*[:/]\s*', '', line, flags=re.IGNORECASE).strip()
            # Remove leading non-alpha noise (like |, >, numbers)
            name_candidate = re.sub(r'^[^A-Za-z]+', '', name_candidate).strip()
            
            if is_valid_name(name_candidate):
                name_candidates.append((name_candidate, name_score(name_candidate)))
        
        # Pick the highest-scoring name
        if name_candidates:
            name_candidates.sort(key=lambda x: x[1], reverse=True)
            entities["name"] = name_candidates[0][0]
    
    # Fallback: labeled name
    if "name" not in entities:
        name_label = re.search(r'(?:Name)\s*[:/]\s*([A-Za-z\s.]+)', text_clean, re.IGNORECASE)
        if name_label:
            candidate = _clean_space(name_label.group(1))
            if is_valid_name(candidate):
                entities["name"] = candidate
    
    # === Gender Inference ===
    # If gender not detected from OCR text, infer from context
    if "gender" not in entities:
        # Check relation patterns: Father/S/O → Male, Husband/W/O → Female
        if re.search(r'(?:Father|S\s*/\s*O|C\s*/\s*O|D\s*/\s*O|पिता)', text_clean, re.IGNORECASE):
            entities["gender"] = "Male"
        elif re.search(r'(?:Husband|W\s*/\s*O|पति)', text_clean, re.IGNORECASE):
            entities["gender"] = "Female"
    
    # === Address ===
    # Aadhaar address usually starts after "Address:" label or after name/DOB section
    addr_match = re.search(
        r'(?:Address|पता)\s*[:/]\s*(.+?)(?=\b\d{4}\s*\d{4}\s*\d{4}\b|\Z)',
        text_clean, re.IGNORECASE | re.DOTALL
    )
    if addr_match:
        raw_addr = _clean_space(addr_match.group(1))
        # Remove trailing Aadhaar number if captured
        raw_addr = re.sub(r'\d{4}\s*\d{4}\s*\d{4}.*$', '', raw_addr).strip()
        if len(raw_addr) > 5:
            entities["address"] = raw_addr
            
            # Parse address into components
            addr_components = _parse_address_components(raw_addr)
            entities.update(addr_components)
    
    # Fallback: find address by pincode pattern
    if "address" not in entities:
        pin_context = re.search(r'([A-Za-z0-9,\s\-/]{10,}?\s*\d{6})', text_clean)
        if pin_context:
            raw_addr = _clean_space(pin_context.group(0))
            entities["address"] = raw_addr
            addr_components = _parse_address_components(raw_addr)
            entities.update(addr_components)
    
    # === Mobile ===
    phone_match = re.search(r'\b(?:\+91[\-\s]?)?([6-9]\d{4}\s?\d{5})\b', text_clean)
    if phone_match:
        entities["mobile"] = phone_match.group(1).replace(" ", "").replace("-", "")
    
    # === Email ===
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_clean)
    if email_match:
        entities["email"] = email_match.group(0).lower()
    
    return entities


def extract_entities(text: str):
    """
    Generic entity extraction (backward compatible).
    Works with PAN cards, birth certificates, voice input, etc.
    """
    entities = {}
    text_clean = text.strip()

    # Email
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text_clean)
    if email_match:
        entities["email"] = email_match.group(0).lower()

    # Phone
    phone_match = re.search(r"\b(?:\+91[\-\s]?)?[6-9]\d{4}\s?\d{5}\b", text_clean)
    if phone_match:
        entities["mobile"] = phone_match.group(0).replace(" ", "").replace("-", "")

    # Gender
    gender_match = re.search(r"\b(Male|Female|Transgender|Man|Woman|पुरुष|महिला)\b", text_clean, re.IGNORECASE)
    if gender_match:
        val = gender_match.group(0)
        if val in ('पुरुष',): val = 'Male'
        elif val in ('महिला',): val = 'Female'
        elif val.capitalize() == "Man": val = "Male"
        elif val.capitalize() == "Woman": val = "Female"
        else: val = val.capitalize()
        entities["gender"] = val

    # Caste
    caste_match = re.search(r"\b(SC|ST|OBC|GEN|General)\b", text_clean, re.IGNORECASE)
    if caste_match:
        val = caste_match.group(0).upper()
        if val == "GENERAL":
            val = "GEN"
        entities["caste"] = val

    # Marital status
    marital_match = re.search(r"\b(Single|Married|Divorced|Widowed)\b", text_clean, re.IGNORECASE)
    if marital_match:
        entities["marital_status"] = marital_match.group(0).capitalize()

    # Aadhaar number
    aadhaar_match = re.search(r"\b\d{4}[\s-]*\d{4}[\s-]*\d{4}\b", text_clean)
    if aadhaar_match:
        entities["aadhaar"] = aadhaar_match.group(0).replace(" ", "").replace("-", "")

    # PAN number
    pan_match = re.search(
        r"\b([A-Z]\s*){5}([0-9]\s*){4}([A-Z])\b",
        text_clean,
        re.IGNORECASE
    )
    if pan_match:
        entities["pan"] = pan_match.group(0).replace(" ", "").upper()

    # DOB — labeled
    dob_labeled = re.search(r"(?:DOB|Date of Birth|born on|D\.O\.B)[\\s:]*(\\d{1,2}[-/\\.]\\d{1,2}[-/\\.]\\d{4})", text_clean, re.IGNORECASE)
    if dob_labeled:
        entities["dob"] = dob_labeled.group(1)
    else:
        # Year of Birth
        yob_match = re.search(r'(?:Year\s*of\s*Birth|YOB)\s*[:/]?\s*(\d{4})', text_clean, re.IGNORECASE)
        if yob_match:
            entities["dob"] = yob_match.group(1)
        else:
            # Spoken DOB
            spoken_dob = re.search(
                r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",
                text_clean, re.IGNORECASE
            )
            if spoken_dob:
                entities["dob"] = spoken_dob.group(1)
            else:
                dob_match = re.search(
                    r"\b(0?[1-9]|[12][0-9]|3[01])[/\-\.](0?[1-9]|1[012])[/\-\.](19|20)\d{2}\b",
                    text_clean
                )
                if dob_match:
                    entities["dob"] = dob_match.group(0)

    # Name — labeled
    name_label_match = re.search(r"(?:Name|Name is|I am|My name is)[\s:]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", text_clean, re.IGNORECASE)
    if name_label_match:
        candidate = name_label_match.group(1).strip()
        if "student" not in candidate.lower() and "here" not in candidate.lower():
            entities["name"] = candidate

    if "name" not in entities:
        name_candidates = re.findall(r"\b([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)+)\b", text_clean)
        blacklist = [
            "INCOME", "TAX", "DEPARTMENT", "GOV", "INDIA", "GOVERNMENT", "MALE", "FEMALE",
            "DOB", "YEAR", "FATHER", "PERMANENT", "ACCOUNT", "NUMBER", "CARD", "DIGITAL",
            "SEVA", "KENDRA", "ADDRESS", "AADHAAR", "MY", "NAME", "IS", "DATE", "BIRTH",
            "PHONE", "CONTACT", "EMAIL", "UIDAI", "UNIQUE", "IDENTIFICATION", "AUTHORITY",
        ]

        for candidate in name_candidates:
            upper_cand = candidate.upper()
            if not any(b in upper_cand.split() for b in blacklist) and len(candidate) > 4:
                entities["name"] = candidate
                break

    # Father name — S/O, D/O, W/O patterns
    relation_match = re.search(
        r'(?:S\s*/\s*O|D\s*/\s*O|W\s*/\s*O|C\s*/\s*O)[.:\s]+([A-Za-z\s.]+?)(?:\n|,|$)',
        text_clean, re.IGNORECASE
    )
    if relation_match and "father_name" not in entities:
        father_name = _clean_space(relation_match.group(1))
        father_name = re.sub(r'\b(Male|Female|DOB|Date|Year|Address)\b.*', '', father_name, flags=re.IGNORECASE).strip()
        if father_name and len(father_name) > 2:
            entities["father_name"] = father_name

    # Father name — "Father :", "पिता :", "Husband :" (Aadhaar card labels)
    if "father_name" not in entities:
        father_label = re.search(
            r'(?:Father(?:\s*(?:\'s)?\s*(?:Name)?)?|पिता|Husband)\s*[:/]\s*([A-Za-z\s.]+?)(?:\n|,|जन्म|DOB|Male|Female|पुरुष|महिला|$)',
            text_clean, re.IGNORECASE
        )
        if father_label:
            father_name = _clean_space(father_label.group(1))
            father_name = re.sub(r'\b(Male|Female|DOB|Date|Year|Address|Birth)\b.*', '', father_name, flags=re.IGNORECASE).strip()
            if father_name and len(father_name) > 2:
                entities["father_name"] = father_name

    # Address — birth certificate style
    bc_addr_match = re.search(r"(?:Address of Parents at the time of birth(?: of the child)?|ADDRESS OF PARENTS AT THE TIME OF BIRTH(?: OF THE CHILD)?)[\s:]+(.+?)(?=\.|Permanent|Address|$)", text_clean, re.IGNORECASE | re.DOTALL)
    if bc_addr_match:
        entities["address"] = _clean_space(bc_addr_match.group(1))

    # Address — conversational
    conv_addr_match = re.search(r"(?:Address is|Live at|Residing at)[\s:]+(.+?)(?=\.|My|Phone|Email|Date|$)", text_clean, re.IGNORECASE)
    if conv_addr_match:
        entities["address"] = _clean_space(conv_addr_match.group(1))

    if "address" not in entities:
        address_match = re.search(r"(?:Address|To)[\s:]+(.*?\d{6})", text_clean, re.DOTALL | re.IGNORECASE)
        if address_match:
            raw_addr = address_match.group(1)
            entities["address"] = _clean_space(raw_addr)
        else:
            pin_match = re.search(r"([A-Za-z0-9,\s\-\/]{15,})\s(\d{6})", text_clean)
            if pin_match:
                entities["address"] = _clean_space(pin_match.group(0))

    # Parse address components if we have an address
    if "address" in entities:
        addr_components = _parse_address_components(entities["address"])
        for key, val in addr_components.items():
            if key not in entities:
                entities[key] = val

    # Registration number
    reg_match = re.search(r"(?:Registration\s*(?:No|Number)|REGISTRATION\s*(?:NO|NUMBER))[\s:]+([A-Z0-9\-\/:]+)", text_clean, re.IGNORECASE)
    if reg_match:
        entities["registration_number"] = _clean_space(reg_match.group(1))

    # Date of registration
    reg_date_match = re.search(r"(?:Date of Registration|REGISTRATION DATE)[\s:]*(\\d{1,2}[-/\\.]\\d{1,2}[-/\\.]\\d{4})", text_clean, re.IGNORECASE)
    if reg_date_match:
        entities["date_of_registration"] = reg_date_match.group(1)

    # Place of birth
    pob_match = re.search(r"(?:Place of Birth|BIRTH PLACE)[\s:]+([A-Za-z\s,]+)(?=\n|Date|Name|$)", text_clean, re.IGNORECASE)
    if pob_match:
        entities["place_of_birth"] = _clean_space(pob_match.group(1))

    # Father name — labeled
    if "father_name" not in entities:
        father_match = re.search(r"(?:Name of Father|Father(?:'s)? Name)[\s:]+([A-Za-z \t\.]+)(?=\n|Name|Address|$)", text_clean, re.IGNORECASE)
        if father_match:
            entities["father_name"] = _clean_space(father_match.group(1))

    # Mother name
    mother_match = re.search(r"(?:Name of Mother|Mother(?:'s)? Name)[\s:]+([A-Za-z \t\.]+)(?=\n|Name|Address|$)", text_clean, re.IGNORECASE)
    if mother_match:
        entities["mother_name"] = _clean_space(mother_match.group(1))

    # Permanent address
    perm_addr_match = re.search(r"(?:Permanent Address(?: of Parents)?|PERMANENT ADDRESS(?: OF PARENTS)?)[\s:]+(.+?)(?=\.|Date|Signature|Registration|REGISTRATION|$)", text_clean, re.IGNORECASE | re.DOTALL)
    if perm_addr_match:
        entities["permanent_address"] = _clean_space(perm_addr_match.group(1))

    return entities
