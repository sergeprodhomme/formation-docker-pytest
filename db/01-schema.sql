-- Schema de la table utilisateurs.
-- Execute automatiquement par Postgres au premier demarrage du conteneur
-- (monte dans /docker-entrypoint-initdb.d/ par docker-compose.yml).

CREATE TABLE IF NOT EXISTS utilisateurs (
    id                  SERIAL PRIMARY KEY,

    -- Donnees d'etat civil (donnees ordinaires, RGPD)
    nom                 VARCHAR(100)  NOT NULL,
    prenom              VARCHAR(100)  NOT NULL,

    -- Courriel en clair : necessaire pour notifier l'utilisateur.
    courriel            VARCHAR(255)  NOT NULL UNIQUE,

    -- HMAC-SHA256 du courriel normalise : sert d'index pseudonymise
    -- (recherche/dedoublonnage sans manipuler l'adresse en clair).
    courriel_hash       CHAR(64)      NOT NULL UNIQUE,

    -- Numero RPPS : chaine de 11 chiffres (evite les pb d'entier > 2^31 etc.)
    -- Le CHECK refuse tout ce qui n'est pas exactement 11 chiffres.
    numero_rpps         CHAR(11)      NOT NULL
        CHECK (numero_rpps ~ '^[0-9]{11}$'),

    -- bcrypt : hache lent, sale (sel integre), dedie aux mots de passe.
    -- 60 caracteres au format $2b$12$...
    mot_de_passe_hash   VARCHAR(60)   NOT NULL,

    cree_le             TIMESTAMPTZ   NOT NULL DEFAULT now(),

    -- Un numero RPPS ne peut etre partage par deux comptes.
    CONSTRAINT rpps_unique UNIQUE (numero_rpps)
);

CREATE INDEX IF NOT EXISTS idx_utilisateurs_courriel_hash ON utilisateurs (courriel_hash);
CREATE INDEX IF NOT EXISTS idx_utilisateurs_nom_prenom ON utilisateurs (nom, prenom);
