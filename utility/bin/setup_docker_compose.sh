#! /usr/bin/env bash

set -e

python manage.py makemigrations
echo "Setup complete: Created migrations."
sleep 2

python manage.py migrate
echo "Setup complete: Applied migrations."
sleep 2

psql -h db -U postgres -d dbachare -c "
INSERT INTO account_user (
    username, email, password, phone_number, last_login, create_time, update_time, is_deleted, is_active, is_admin, is_staff, is_superuser
) VALUES
    ('user1', 'user1@gmail.com', 'password@1', '09128355701', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user2', 'user2@gmail.com', 'password@2', '09128355702', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user3', 'user3@gmail.com', 'password@3', '09128355703', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user4', 'user4@gmail.com', 'password@4', '09128355704', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE),
    ('user5', 'user5@gmail.com', 'password@5', '09128355705', NULL, NOW(), NOW(), FALSE, TRUE, FALSE, FALSE, FALSE);
"
echo "Database setup complete."

echo "Creating superuser..."
python manage.py creat_a_super_user --username PedraKmarimi --email pedram.9060@gmail.com --password qwertyQ@1 --phone_number 09128355747
echo "setup complete creat a super user."
sleep 2

echo "Starting Django development server..."
