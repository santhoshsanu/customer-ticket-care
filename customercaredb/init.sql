CREATE TABLE IF NOT EXISTS tickets (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    complaint_text text NOT NULL,
    product_hint text,
    category text NOT NULL CHECK (category IN (
        'product_defect',
        'warranty_claim',
        'installation_support',
        'software_issue',
        'shipping_damage',
        'returns_refunds',
        'billing',
        'general_inquiry'
    )),
    priority text NOT NULL CHECK (priority IN (
        'low', 'medium', 'high', 'critical'
    )),
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS known_resolutions (
    search_phrase text PRIMARY KEY,
    resolution text NOT NULL
);

INSERT INTO known_resolutions (search_phrase, resolution)
VALUES
    ('headphones not pairing', 'Forget the headphones in Bluetooth settings, put them into pairing mode, then pair them again.'),
    ('headphones are not pairing', 'Forget the headphones in Bluetooth settings, put them into pairing mode, then pair them again.'),
    ('bluetooth pairing', 'Forget the headphones in Bluetooth settings, put them into pairing mode, then pair them again.'),
    ('tablet will not charge', 'Try a compatible charger and cable and leave the tablet connected for 30 minutes.')
ON CONFLICT (search_phrase) DO NOTHING;
