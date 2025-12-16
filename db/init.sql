BEGIN;

CREATE TABLE Passwords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash VARCHAR(256) NOT NULL,
    salt VARCHAR(256) NOT NULL,
    algorithm VARCHAR(32) NOT NULL,
    number_of_passes INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    profile_picture_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    last_login TIMESTAMP,
    password_id UUID UNIQUE,
    FOREIGN KEY (password_id) REFERENCES Passwords(id)
);

CREATE TABLE Groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_picture_url VARCHAR(500),
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES Users(id)
);

CREATE TABLE Group_Roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    permissions JSONB,
    group_id UUID NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE CASCADE
);

CREATE TABLE Group_Members (
    group_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    invited_by UUID,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Group_Roles(id),
    FOREIGN KEY (invited_by) REFERENCES Users(id)
);

CREATE TABLE Notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    color_hex VARCHAR(7),
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES Users(id)
);

CREATE TABLE Note_Access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL,
    user_id UUID,
    group_id UUID,
    access_level VARCHAR(20) NOT NULL CHECK (access_level IN ('read', 'write', 'admin')),
    granted_by UUID NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (note_id, user_id, group_id),
    CHECK (
        (user_id IS NOT NULL AND group_id IS NULL) OR
        (user_id IS NULL AND group_id IS NOT NULL)
    ),
    FOREIGN KEY (note_id) REFERENCES Notes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES Users(id)
);

CREATE TABLE Tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    color_hex VARCHAR(7),
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, created_by),
    FOREIGN KEY (created_by) REFERENCES Users(id)
);

CREATE TABLE Note_Tags (
    note_id UUID NOT NULL,
    tag_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES Notes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
);

CREATE TABLE Revoked_Tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(256) NOT NULL UNIQUE,
    user_id UUID NOT NULL,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL, 
    reason VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
COMMIT;

CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_created_at ON Users(created_at);
CREATE INDEX idx_users_is_deleted ON Users(is_deleted);

CREATE INDEX idx_passwords_created_at ON Passwords(created_at);

CREATE INDEX idx_groups_created_by ON Groups(created_by);
CREATE INDEX idx_groups_created_at ON Groups(created_at);
CREATE INDEX idx_groups_is_deleted ON Groups(is_deleted);

CREATE INDEX idx_group_roles_group ON Group_Roles(group_id);
CREATE INDEX idx_group_roles_default ON Group_Roles(is_default);

CREATE INDEX idx_group_members_user ON Group_Members(user_id);
CREATE INDEX idx_group_members_role ON Group_Members(role_id);
CREATE INDEX idx_group_members_active ON Group_Members(is_active);

CREATE INDEX idx_notes_created_by ON Notes(created_by);
CREATE INDEX idx_notes_created_at ON Notes(created_at);
CREATE INDEX idx_notes_location ON Notes(latitude, longitude);
CREATE INDEX idx_notes_is_deleted ON Notes(is_deleted);
CREATE INDEX idx_notes_updated_at ON Notes(updated_at);

CREATE INDEX idx_note_access_note ON Note_Access(note_id);
CREATE INDEX idx_note_access_user ON Note_Access(user_id);
CREATE INDEX idx_note_access_group ON Note_Access(group_id);
CREATE INDEX idx_note_access_level ON Note_Access(access_level);

CREATE INDEX idx_tags_created_by ON Tags(created_by);
CREATE INDEX idx_tags_name ON Tags(name);

CREATE INDEX idx_note_tags_note ON Note_Tags(note_id);
CREATE INDEX idx_note_tags_tag ON Note_Tags(tag_id);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON Users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON Groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON Notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
