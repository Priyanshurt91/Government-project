import copy


# Alias mappings: extracted entity key -> possible form field keys
FIELD_ALIASES = {
    "name": ["name", "full_name", "applicant_name"],
    "father_name": ["father_name", "father's_name", "guardian_name"],
    "mother_name": ["mother_name", "mother's_name"],
    "dob": ["dob", "date_of_birth"],
    "gender": ["gender", "sex"],
    "aadhaar": ["aadhaar", "aadhar", "aadhaar_number", "uid"],
    "pan": ["pan", "pan_number"],
    "mobile": ["mobile", "phone", "mobile_number", "contact"],
    "email": ["email", "email_address"],
    "address": ["address", "current_address", "correspondence_address"],
    "permanent_address": ["permanent_address", "perm_address"],
    "pincode": ["pincode", "pin_code", "zip"],
    "district": ["district"],
    "state": ["state"],
    "village": ["village", "city", "town"],
    "taluka": ["taluka", "tehsil"],
    "caste": ["caste", "caste_category"],
    "caste_name": ["caste_name"],
    "sub_caste": ["sub_caste"],
    "marital_status": ["marital_status"],
    "place_of_birth": ["place_of_birth", "birth_place"],
    "registration_number": ["registration_number", "reg_no"],
    "date_of_registration": ["date_of_registration", "reg_date"],
    "father_caste": ["father_caste"],
}


def _build_reverse_alias_map():
    """Build a reverse map: form field name -> entity key."""
    reverse = {}
    for entity_key, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            reverse[alias.lower()] = entity_key
    return reverse


def map_to_form(entities, form_template):
    """
    Map extracted entities to form template fields.
    Uses alias mappings for flexible matching.
    """
    filled_form = copy.deepcopy(form_template)
    reverse_map = _build_reverse_alias_map()

    target_dict = filled_form
    if "fields" in filled_form and isinstance(filled_form["fields"], dict):
        target_dict = filled_form["fields"]

    for field in target_dict:
        field_lower = field.lower()

        # Direct match
        if field in entities:
            target_dict[field] = entities[field]
            continue

        # Case-insensitive match
        for ent_key, ent_val in entities.items():
            if ent_key.lower() == field_lower:
                target_dict[field] = ent_val
                break
        else:
            # Alias match: check if this form field is an alias for any entity
            entity_key = reverse_map.get(field_lower)
            if entity_key and entity_key in entities:
                target_dict[field] = entities[entity_key]

    return filled_form
