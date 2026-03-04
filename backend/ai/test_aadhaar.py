"""
Test script for Aadhaar card entity extraction.
Tests both the Aadhaar-specific extractor and the generic extractor
with simulated Aadhaar OCR text.
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding='utf-8')

from ai.entity_extractor import extract_entities_aadhaar, extract_entities


def test_aadhaar_extraction():
    """Test with typical Aadhaar card OCR text."""
    
    # Simulated OCR output from an Aadhaar card
    aadhaar_text = """
    Government of India
    
    John Kumar
    DOB: 15/08/1990
    Male
    
    S/O Rajesh Kumar
    
    Address: 42, MG Road, Sector 5,
    Koramangala, Bangalore,
    Karnataka 560095
    
    1234 5678 9012
    """
    
    print("=" * 60)
    print("TEST 1: Aadhaar Card with DOB")
    print("=" * 60)
    
    entities = extract_entities_aadhaar(aadhaar_text)
    print(f"\nExtracted Entities: {entities}\n")
    
    expected = {
        "name": "John Kumar",
        "dob": "15/08/1990",
        "gender": "Male",
        "father_name": "Rajesh Kumar",
        "aadhaar": "123456789012",
        "pincode": "560095",
    }
    
    check_results(entities, expected)


def test_aadhaar_yob():
    """Test with Aadhaar card showing Year of Birth instead of DOB."""
    
    aadhaar_text = """
    Government of India
    
    Priya Sharma
    Year of Birth: 1995
    Female
    
    D/O Ram Sharma
    
    Address: House No 123, Village Rampur,
    Dist. Varanasi,
    Uttar Pradesh 221001
    
    9876 5432 1098
    """
    
    print("\n" + "=" * 60)
    print("TEST 2: Aadhaar Card with Year of Birth")
    print("=" * 60)
    
    entities = extract_entities_aadhaar(aadhaar_text)
    print(f"\nExtracted Entities: {entities}\n")
    
    expected = {
        "name": "Priya Sharma",
        "dob": "1995",
        "gender": "Female",
        "father_name": "Ram Sharma",
        "aadhaar": "987654321098",
        "pincode": "221001",
        "state": "Uttar Pradesh",
    }
    
    check_results(entities, expected)


def test_generic_extractor_with_aadhaar():
    """Test that the generic extractor also handles Aadhaar patterns."""
    
    aadhaar_text = """
    Amit Verma
    S/O Suresh Verma
    DOB: 01/01/1985
    Male
    Address: 56 Park Street, Kolkata, West Bengal 700016
    4567 8901 2345
    """
    
    print("\n" + "=" * 60)
    print("TEST 3: Generic Extractor with Aadhaar Text")
    print("=" * 60)
    
    entities = extract_entities(aadhaar_text)
    print(f"\nExtracted Entities: {entities}\n")
    
    expected = {
        "aadhaar": "456789012345",
        "gender": "Male",
        "father_name": "Suresh Verma",
    }
    
    check_results(entities, expected)


def test_birth_cert_still_works():
    """Verify existing birth certificate extraction still works."""
    
    text = """
    GOVERNMENT OF MAHARASHTRA
    DEPARTMENT OF HEALTH
    BIRTH CERTIFICATE
    
    NAME: ABHAYRAJ SHEKHAR THORAT   SEX: MALE
    DATE OF BIRTH: 12-05-2020
    
    NAME OF FATHER: SHEKHAR GOPAL THORAT
    NAME OF MOTHER: SHITAL SHEKHAR THORAT
    
    Address of Parents at the time of birth of the child:
    TASGAON, SANGLI, MAHARASHTRA 416312
    """
    
    print("\n" + "=" * 60)
    print("TEST 4: Birth Certificate (backward compat)")
    print("=" * 60)
    
    entities = extract_entities(text)
    print(f"\nExtracted Entities: {entities}\n")
    
    expected = {
        "gender": "Male",
        "dob": "12-05-2020",
        "father_name": "SHEKHAR GOPAL THORAT",
        "mother_name": "SHITAL SHEKHAR THORAT",
    }
    
    check_results(entities, expected)


def check_results(entities, expected):
    """Check extracted entities against expected values."""
    passed = True
    for key, expected_val in expected.items():
        actual_val = entities.get(key, "")
        # Normalize for comparison
        norm_expected = " ".join(str(expected_val).split())
        norm_actual = " ".join(str(actual_val).split())
        
        if norm_actual == norm_expected:
            print(f"  ✅ {key}: {actual_val}")
        else:
            print(f"  ❌ {key}: expected '{expected_val}', got '{actual_val}'")
            passed = False
    
    if passed:
        print("\n  🎉 ALL CHECKS PASSED")
    else:
        print("\n  ⚠️ SOME CHECKS FAILED")
    
    return passed


if __name__ == "__main__":
    test_aadhaar_extraction()
    test_aadhaar_yob()
    test_generic_extractor_with_aadhaar()
    test_birth_cert_still_works()
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
