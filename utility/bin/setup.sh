#! /usr/bin/env bash

docker rm -f dbachare

docker run --name dbachare -e POSTGRES_PASSWORD=1234 -d -p "5432:5432" -e PGDATA=/var/lib/postgresql/data/pgdatadbachare -v /docker/db:/var/lib/postgresql/data postgres:alpine

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
RETRIES=10
until docker exec -i dbachare pg_isready -U postgres || [ $RETRIES -eq 0 ]; do
  echo "Waiting for PostgreSQL server, $((RETRIES--)) remaining attempts..."
  sleep 2
done

if [ $RETRIES -eq 0 ]; then
  echo "PostgreSQL did not start in time."
  exit 1
fi


docker exec -i dbachare psql -U postgres -d dbachare -c "
DROP TABLE IF EXISTS account_user CASCADE;
DROP TABLE IF EXISTS account_user_groups CASCADE;
DROP TABLE IF EXISTS account_user_user_permissions CASCADE;
DROP TABLE IF EXISTS account_userauth CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS authtoken_token CASCADE;
DROP TABLE auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
"

echo "Setup complete: Dropped tables."
sleep 2


python manage.py makemigrations
echo "Setup complete: Created migrations."
sleep 2

python manage.py migrate
echo "Setup complete: Applied migrations."
sleep 2




docker exec -i dbachare psql -U postgres -d dbachare -c "
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
if [ $? -ne 0 ]; then
  echo "Failed to create superuser."
  exit 1
fi
echo "setup complete creat a super user."
sleep 2

echo "Starting Django development server..."
python manage.py runserver