# === Custom Entity Patterns ===
PRIMARY_PATTERNS = [
    {"label": "SUM", "pattern": [{"TEXT": "Sumário"}, {"TEXT": ":", "OP": "!"}]},
    {"label": "SUM:", "pattern": [{"TEXT": "Sumário"}]},
    # ⬇️  Replace the old DES block with this pattern
    # --- replace the old “DES” block with this ---
    {
    "label": "DES",
    "pattern": [
        {   # header must start the sentence / line
            "LOWER": {"IN": ["despacho", "aviso", "declaração", "edital", "deliberação", "contrato"]}
        },
        {   # optional words between the header and “n.º”
            "LOWER": {"IN": ["conjunto", "de", "da", "do",
                             "retificação", "retificacao"]},
            "OP": "*"
        },
        {   # mandatory “n.º” (or “nº”)
            "TEXT": {"IN": ["n.º", "nº"]}
        },
        { "LIKE_NUM": True },          # e.g. 47, 128, 16
        #{ "TEXT": "/", "OP": "?" },    # optional slash
       # { "LIKE_NUM": True, "OP": "?" },# e.g. /2025
        { "IS_PUNCT": True, "OP": "!" }
    ]
},
     {
        "label": "HEADER_DATE_CORRESPONDENCIA",
        "pattern": [
            {"LIKE_NUM": True},
            {"IS_PUNCT": True, "TEXT": "-"},
            {"IS_ALPHA": True, "LENGTH": 1},
            {"IS_SPACE": True, "OP": "?"},
            {"LIKE_NUM": True},
            {"LOWER": "de"},
            {"LOWER": {"IN": [
                "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ]}},
            {"LOWER": "de"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"LOWER": "número"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"TEXT": {"REGEX": "^CORRESPONDÊNCIA$"}}
        ]
    },
    {
        "label": "HEADER_DATE_CORRESPONDENCIA",
        "pattern": [
            {"LIKE_NUM": True},
            {"LOWER": "de"},
            {"LOWER": {"IN": [
                "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ]}},
            {"LOWER": "de"},
            {"LIKE_NUM": True},
            {"IS_ALPHA": True, "LENGTH": 1},
            {"IS_PUNCT": True, "TEXT": "-"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"LOWER": "número"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"TEXT": {"REGEX": "^CORRESPONDÊNCIA$"}}

        ]
    },



    {
        "label": "HEADER_DATE",
        "pattern": [
            {"LIKE_NUM": True},
            {"IS_PUNCT": True, "TEXT": "-"},
            {"IS_ALPHA": True, "LENGTH": 1},
            {"IS_SPACE": True, "OP": "?"},
            {"LIKE_NUM": True},
            {"LOWER": "de"},
            {"LOWER": {"IN": [
                "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ]}},
            {"LOWER": "de"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"LOWER": "número"},
            {"LIKE_NUM": True},
        ]
    },
    {
        "label": "HEADER_DATE",
        "pattern": [
            {"LIKE_NUM": True},
            {"LOWER": "de"},
            {"LOWER": {"IN": [
                "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ]}},
            {"LOWER": "de"},
            {"LIKE_NUM": True},
            {"IS_ALPHA": True, "LENGTH": 1},
            {"IS_PUNCT": True, "TEXT": "-"},
            {"LIKE_NUM": True},
            {"TEXT": {"REGEX": "^[\\n\\r]+$"}, "OP": "*"},  # newline token(s)
            {"LOWER": "número"},
            {"LIKE_NUM": True}

        ]
    },
   {
    "label": "SECRETARIA",
    "pattern": [
        {"TEXT": {"IN": ["PRESIDÊNCIA", "SECRETARIA", "CÂMARA"]}},       # anchor on SECRETARIA
        {"IS_UPPER": True, "OP": "+"}, 
         {"IS_PUNCT": True, "OP": "*"},
        {"TEXT": "\n", "OP": "?"},
         {"IS_PUNCT": True, "OP": "*"},
        {"IS_UPPER": True, "OP": "+"},
    ]
}



,
    

]

COMPOSED_PATTERNS = [
    {
    "label": "SEC_DES_SUM",
    "pattern": [
        {"IS_UPPER": True, "OP": "+"},
        {"IS_SPACE": True, "OP": "*"},
        {"IS_UPPER": True, "OP": "+"},
        {"IS_SPACE": True, "OP": "*"},
        {"LOWER": {"IN": ["despacho", "aviso"]}},
        {"IS_SPACE": True, "OP": "*"},
        {"TEXT": "n.º", "OP": "?"},
        {"IS_SPACE": True, "OP": "*"},
        {"LIKE_NUM": True},
        {"IS_SPACE": True, "OP": "*"},
        {"TEXT": "Sumário"},
        {"TEXT": ":", "OP": "?"}
    ]
}


]

