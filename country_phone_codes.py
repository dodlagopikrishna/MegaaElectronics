"""ITU E.164 country calling codes for client phone fields."""

DEFAULT_COUNTRY_CODE = "+91"


def country_option_label(code: str, name: str) -> str:
    """Dropdown label: country name with dial code."""
    return f"{name} ({code})"

# (dial_code, country/territory name) — sorted by country name
COUNTRY_CODES = [
    ("+93", "Afghanistan"),
    ("+355", "Albania"),
    ("+213", "Algeria"),
    ("+376", "Andorra"),
    ("+244", "Angola"),
    ("+1268", "Antigua and Barbuda"),
    ("+54", "Argentina"),
    ("+374", "Armenia"),
    ("+61", "Australia"),
    ("+43", "Austria"),
    ("+994", "Azerbaijan"),
    ("+1242", "Bahamas"),
    ("+973", "Bahrain"),
    ("+880", "Bangladesh"),
    ("+1246", "Barbados"),
    ("+375", "Belarus"),
    ("+32", "Belgium"),
    ("+501", "Belize"),
    ("+229", "Benin"),
    ("+975", "Bhutan"),
    ("+591", "Bolivia"),
    ("+387", "Bosnia and Herzegovina"),
    ("+267", "Botswana"),
    ("+55", "Brazil"),
    ("+673", "Brunei"),
    ("+359", "Bulgaria"),
    ("+226", "Burkina Faso"),
    ("+257", "Burundi"),
    ("+855", "Cambodia"),
    ("+237", "Cameroon"),
    ("+1", "Canada"),
    ("+238", "Cape Verde"),
    ("+236", "Central African Republic"),
    ("+235", "Chad"),
    ("+56", "Chile"),
    ("+86", "China"),
    ("+57", "Colombia"),
    ("+269", "Comoros"),
    ("+242", "Congo"),
    ("+243", "Congo (DRC)"),
    ("+506", "Costa Rica"),
    ("+385", "Croatia"),
    ("+53", "Cuba"),
    ("+357", "Cyprus"),
    ("+420", "Czech Republic"),
    ("+45", "Denmark"),
    ("+253", "Djibouti"),
    ("+1767", "Dominica"),
    ("+1809", "Dominican Republic"),
    ("+593", "Ecuador"),
    ("+20", "Egypt"),
    ("+503", "El Salvador"),
    ("+240", "Equatorial Guinea"),
    ("+291", "Eritrea"),
    ("+372", "Estonia"),
    ("+268", "Eswatini"),
    ("+251", "Ethiopia"),
    ("+679", "Fiji"),
    ("+358", "Finland"),
    ("+33", "France"),
    ("+241", "Gabon"),
    ("+220", "Gambia"),
    ("+995", "Georgia"),
    ("+49", "Germany"),
    ("+233", "Ghana"),
    ("+30", "Greece"),
    ("+1473", "Grenada"),
    ("+502", "Guatemala"),
    ("+224", "Guinea"),
    ("+245", "Guinea-Bissau"),
    ("+592", "Guyana"),
    ("+509", "Haiti"),
    ("+504", "Honduras"),
    ("+852", "Hong Kong"),
    ("+36", "Hungary"),
    ("+354", "Iceland"),
    ("+91", "India"),
    ("+62", "Indonesia"),
    ("+98", "Iran"),
    ("+964", "Iraq"),
    ("+353", "Ireland"),
    ("+972", "Israel"),
    ("+39", "Italy"),
    ("+225", "Ivory Coast"),
    ("+1876", "Jamaica"),
    ("+81", "Japan"),
    ("+962", "Jordan"),
    ("+7", "Kazakhstan"),
    ("+254", "Kenya"),
    ("+686", "Kiribati"),
    ("+965", "Kuwait"),
    ("+996", "Kyrgyzstan"),
    ("+856", "Laos"),
    ("+371", "Latvia"),
    ("+961", "Lebanon"),
    ("+266", "Lesotho"),
    ("+231", "Liberia"),
    ("+218", "Libya"),
    ("+423", "Liechtenstein"),
    ("+370", "Lithuania"),
    ("+352", "Luxembourg"),
    ("+853", "Macau"),
    ("+261", "Madagascar"),
    ("+265", "Malawi"),
    ("+60", "Malaysia"),
    ("+960", "Maldives"),
    ("+223", "Mali"),
    ("+356", "Malta"),
    ("+692", "Marshall Islands"),
    ("+222", "Mauritania"),
    ("+230", "Mauritius"),
    ("+52", "Mexico"),
    ("+691", "Micronesia"),
    ("+373", "Moldova"),
    ("+377", "Monaco"),
    ("+976", "Mongolia"),
    ("+382", "Montenegro"),
    ("+212", "Morocco"),
    ("+258", "Mozambique"),
    ("+95", "Myanmar"),
    ("+264", "Namibia"),
    ("+674", "Nauru"),
    ("+977", "Nepal"),
    ("+31", "Netherlands"),
    ("+64", "New Zealand"),
    ("+505", "Nicaragua"),
    ("+227", "Niger"),
    ("+234", "Nigeria"),
    ("+850", "North Korea"),
    ("+389", "North Macedonia"),
    ("+47", "Norway"),
    ("+968", "Oman"),
    ("+92", "Pakistan"),
    ("+680", "Palau"),
    ("+970", "Palestine"),
    ("+507", "Panama"),
    ("+675", "Papua New Guinea"),
    ("+595", "Paraguay"),
    ("+51", "Peru"),
    ("+63", "Philippines"),
    ("+48", "Poland"),
    ("+351", "Portugal"),
    ("+974", "Qatar"),
    ("+40", "Romania"),
    ("+7", "Russia"),
    ("+250", "Rwanda"),
    ("+1869", "Saint Kitts and Nevis"),
    ("+1758", "Saint Lucia"),
    ("+1784", "Saint Vincent and the Grenadines"),
    ("+685", "Samoa"),
    ("+378", "San Marino"),
    ("+239", "Sao Tome and Principe"),
    ("+966", "Saudi Arabia"),
    ("+221", "Senegal"),
    ("+381", "Serbia"),
    ("+248", "Seychelles"),
    ("+232", "Sierra Leone"),
    ("+65", "Singapore"),
    ("+421", "Slovakia"),
    ("+386", "Slovenia"),
    ("+677", "Solomon Islands"),
    ("+252", "Somalia"),
    ("+27", "South Africa"),
    ("+82", "South Korea"),
    ("+211", "South Sudan"),
    ("+34", "Spain"),
    ("+94", "Sri Lanka"),
    ("+249", "Sudan"),
    ("+597", "Suriname"),
    ("+46", "Sweden"),
    ("+41", "Switzerland"),
    ("+963", "Syria"),
    ("+886", "Taiwan"),
    ("+992", "Tajikistan"),
    ("+255", "Tanzania"),
    ("+66", "Thailand"),
    ("+670", "Timor-Leste"),
    ("+228", "Togo"),
    ("+676", "Tonga"),
    ("+1868", "Trinidad and Tobago"),
    ("+216", "Tunisia"),
    ("+90", "Turkey"),
    ("+993", "Turkmenistan"),
    ("+688", "Tuvalu"),
    ("+256", "Uganda"),
    ("+380", "Ukraine"),
    ("+971", "United Arab Emirates"),
    ("+44", "United Kingdom"),
    ("+1", "United States"),
    ("+598", "Uruguay"),
    ("+998", "Uzbekistan"),
    ("+678", "Vanuatu"),
    ("+379", "Vatican City"),
    ("+58", "Venezuela"),
    ("+84", "Vietnam"),
    ("+967", "Yemen"),
    ("+260", "Zambia"),
    ("+263", "Zimbabwe"),
]

# NiceGUI select options: {'value': 'label'} — value is dial code, label shows country name
PHONE_CODE_SELECT = {code: country_option_label(code, name) for code, name in COUNTRY_CODES}

# List form for selects that use string values (avoids duplicate +1 / +7 keys in dict)
PHONE_CODE_OPTIONS = [country_option_label(code, name) for code, name in COUNTRY_CODES]
LABEL_TO_CODE = {label: code for code, name in COUNTRY_CODES for label in [country_option_label(code, name)]}
DEFAULT_PHONE_LABEL = country_option_label(DEFAULT_COUNTRY_CODE, "India")

_DIAL_CODES_BY_LENGTH = sorted({code for code, _ in COUNTRY_CODES}, key=len, reverse=True)


def dial_code_to_label(code: str) -> str:
    """Map dial code to dropdown label (first match if code is shared)."""
    for dial, name in COUNTRY_CODES:
        if dial == code:
            return country_option_label(dial, name)
    return country_option_label(code, "Unknown")


def dial_code_from_selection(selection: str) -> str:
    """Resolve dial code from dropdown value or typed filter text."""
    selection = (selection or "").strip()
    if not selection:
        return DEFAULT_COUNTRY_CODE
    if selection in LABEL_TO_CODE:
        return LABEL_TO_CODE[selection]
    if selection in PHONE_CODE_SELECT:
        return selection
    if selection.startswith("+"):
        token = selection.split()[0]
        if token in PHONE_CODE_SELECT:
            return token
        return token
    if selection.endswith(")") and "(" in selection:
        part = selection[selection.rfind("(") + 1 : -1]
        if part.startswith("+"):
            return part
    return DEFAULT_COUNTRY_CODE


def parse_phone(phone: str) -> tuple[str, str]:
    """Split stored phone into (country_code, local_number)."""
    phone = (phone or "").strip()
    if not phone:
        return DEFAULT_COUNTRY_CODE, ""

    normalized = phone.replace("(", "").replace(")", "").replace("-", " ")
    for code in _DIAL_CODES_BY_LENGTH:
        if normalized.startswith(code):
            rest = normalized[len(code) :].strip(" -.")
            return code, rest

    if normalized.startswith("+"):
        parts = normalized.split(None, 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], ""

    return DEFAULT_COUNTRY_CODE, phone


def format_phone(country_code: str, number: str) -> str:
    """Combine country code and local number for storage/display."""
    number = (number or "").strip()
    code = (country_code or DEFAULT_COUNTRY_CODE).strip()
    if not number:
        return ""
    return f"{code} {number}"
