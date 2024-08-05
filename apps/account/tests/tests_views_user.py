from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserListAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='PedramKarimi',
            email='pedram.9060@gmail.com',
            phone_number='09128355747',
            password='qwertyQ@1'
        )
        self.normal_user = User.objects.create_user(
            username='PedramKarimiUser',
            email='pedramuser.9060@gmail.com',
            phone_number='09128355740',
            password='qwertyQ@1'
        )
        self.url = reverse('user-list')

        self.admin_token = RefreshToken.for_user(self.admin_user).access_token  # noqa
        self.normal_token = RefreshToken.for_user(self.normal_user).access_token  # noqa

    def test_user_list_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_user_list_as_normal_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.normal_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_filter_by_active_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(user['is_active'] for user in response.data['results']))

        response = self.client.get(self.url, {'is_active': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(not user['is_active'] for user in response.data['results']))


class DetailAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='PedramKarimi',
            email='pedram.9060@gmail.com',
            phone_number='09128355747',
            password='qwertyQ@1'
        )
        self.normal_user = User.objects.create_user(
            username='PedramKarimiUser',
            email='pedramuser.9060@gmail.com',
            phone_number='09128355740',
            password='qwertyQ@1'
        )
        self.other_user = User.objects.create_user(
            username='PedramKarimiother',
            email='pedramother.9060@gmail.com',
            phone_number='09128355741',
            password='qwertyQ@1'
        )

        self.admin_token = RefreshToken.for_user(self.admin_user).access_token  # noqa
        self.normal_token = RefreshToken.for_user(self.normal_user).access_token  # noqa
        self.other_token = RefreshToken.for_user(self.other_user).access_token  # noqa

    def test_retrieve_user_details_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')  # noqa
        url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.normal_user.email)

    def test_retrieve_own_details(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.normal_token}')  # noqa
        url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.normal_user.email)

    def test_retrieve_other_user_details_as_normal_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.normal_token}')
        url = reverse('user-detail', kwargs={'pk': self.other_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_details_unauthenticated(self):
        url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username='PedramKarimi',
            email='pedram.9060@gmail.com',
            phone_number='09128355747',
            password='qwertyQ@1'
        )
        self.user = User.objects.create_user(
            username='PedramKarimiUser',
            email='pedramuser.9060@gmail.com',
            phone_number='09128355740',
            password='qwertyQ@1'
        )

        self.user_token = RefreshToken.for_user(self.user).access_token  # noqa
        self.admin_token = RefreshToken.for_user(self.admin_user).access_token  # noqa

        self.url = reverse('user-change-password', kwargs={'pk': self.user.pk})
        self.valid_payload = {
            'old_password': 'qwertyQ@1',
            'new_password1': 'newPasswordQ@2',
            'new_password2': 'newPasswordQ@2'
        }
        self.invalid_payload = {
            'old_password': 'wrongpassword',
            'new_password1': 'newPasswordQ@2',
            'new_password2': 'newPasswordQ@2'
        }

    def test_change_password_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_change_password_wrong_old_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.put(self.url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertEqual(response.data['old_password'][0], 'Wrong password.')

    def test_change_password_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_change_password_unauthenticated(self):
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_by_other_user(self):
        other_user = User.objects.create_user(
            username='OtherUser',
            email='otheruser@example.com',
            phone_number='09128355748',
            password='otheruserpassword'
        )
        other_user_token = RefreshToken.for_user(other_user).access_token  # noqa
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_user_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserUpdateAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()  # noqa

        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@gmail.com',
            phone_number='09128355747',
            password='adminpassword'
        )
        self.user = User.objects.create_user(
            username='regularuser',
            email='user@gmail.com',
            phone_number='09128355740',
            password='userpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@gmail.com',
            phone_number='09128355748',
            password='otherpassword'
        )

        self.user_token = RefreshToken.for_user(self.user).access_token  # noqa
        self.admin_token = RefreshToken.for_user(self.admin_user).access_token  # noqa
        self.other_user_token = RefreshToken.for_user(self.other_user).access_token  # noqa

        self.url = reverse('user-update', kwargs={'pk': self.user.pk})
        self.valid_payload = {
            'username': 'updateduser',
            'email': 'updateduser@gmail.com',
            'phone_number': '09128355749'
        }
        self.invalid_payload = {
            'username': '',
            'email': 'updateduser@gmail.com',
            'phone_number': '09128355749'
        }

    def test_update_user_details_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.valid_payload['username'])

    def test_update_user_details_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.valid_payload['username'])

    def test_update_user_details_unauthenticated(self):
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_details_by_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_user_token}')
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserDeleteAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()  # noqa

        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@gmail.com',
            phone_number='09128355747',
            password='adminpassword'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@gmail.com',
            phone_number='09128355740',
            password='userpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@gmail.com',
            phone_number='09128355748',
            password='otherpassword'
        )

        self.regular_user_token = RefreshToken.for_user(self.regular_user).access_token  # noqa
        self.admin_token = RefreshToken.for_user(self.admin_user).access_token  # noqa
        self.other_user_token = RefreshToken.for_user(self.other_user).access_token  # noqa

        self.url = reverse('user-delete', kwargs={'pk': self.regular_user.pk})

    def test_delete_user_by_self(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.regular_user.pk).exists())

    def test_delete_user_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.regular_user.pk).exists())

    def test_delete_user_by_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_user_token}')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existent_user(self):
        non_existent_url = reverse('user-delete', kwargs={'pk': 9999})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_unauthenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
