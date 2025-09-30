import pytest
from models.userdata import UserData
from models.contact_form import ContactFormData
from models.felling_form import FellingFormData

@pytest.fixture
def empty_userdata():
    """Fixture to create a fresh UserData object for each test"""
    return UserData()

# Test 1 : Default Values
def test_userdata_defaults(empty_userdata):
    u = empty_userdata
    assert u.preferred_language is None
    assert u.language_selected is False
    assert u.awaiting_confirmation is False
    assert u.should_submit is False
    assert isinstance(u.contact_form,ContactFormData)
    assert isinstance(u.felling_form,FellingFormData)
    assert u.agent_type is None
    assert u.agents == {}
    assert u.prev_agent is None
    assert u.requested_route is None


# Test 2: Updating conversation state
def test_conversation_state_updates(empty_userdata):
    u = empty_userdata
    u.preferred_language = "english"
    u.language_selected = True
    u.awaiting_confirmation = True
    u.should_submit = True

    assert u.preferred_language == "english"
    assert u.language_selected is True
    assert u.awaiting_confirmation is True
    assert u.should_submit is True

# Test 3: Current form logic based on agent_type
def test_current_form_selection(empty_userdata):
    u = empty_userdata

    # Contact agent
    u.agent_type = "contact"
    assert u.current_form == u.contact_form

    # Felling agent
    u.agent_type = "felling"
    assert u.current_form == u.felling_form

    # Greeter or None
    u.agent_type = "greeter"
    assert u.current_form is None
    u.agent_type = None
    assert u.current_form is None

# Test 4: Filling contact form
def test_contact_form_filling(empty_userdata):
    u = empty_userdata
    u.agent_type = "contact"
    form = u.current_form
    assert isinstance(form, ContactFormData)

    # Fill required fields
    form.company = "ACME Corp"
    form.subject = "Lost ID"
    form.message = "Please help with lost ID"
    form.phone = "1234567890"

    # Assertions
    for field in form.required_fields:
        assert getattr(form, field) is not None

# Test 5: Filling felling form
def test_felling_form_filling(empty_userdata):
    u = empty_userdata
    u.agent_type = "felling"
    form = u.current_form
    assert isinstance(form, FellingFormData)

    # Fill required fields
    for field in form.required_fields:
        setattr(form, field, f"test_{field}")

    # Fill required flags
    for flag in getattr(form, "required_flags", []):
        setattr(form, flag, True)

    # Assertions for fields
    for field in form.required_fields:
        assert getattr(form, field).startswith("test_")

    # Assertions for flags
    for flag in getattr(form, "required_flags", []):
        assert getattr(form, flag) is True

# Test 6: Partial filling
def test_partial_form_defaults(empty_userdata):
    u = empty_userdata

    # Contact form partial
    u.agent_type = "contact"
    form = u.current_form
    assert form.company is None
    assert form.message is None

    # Felling form partial
    u.agent_type = "felling"
    form = u.current_form
    assert form.files_uploaded == {}
    assert form.agree_terms is False