from django.contrib.auth.models import User
from django.test import TestCase
from superflatpages.models import FlatPage, FlatPageSnapshot


class SnapshotTestCase(TestCase):
    def setUp(self):
        super(SnapshotTestCase, self).setUp()
        self.user = User.objects.create_user('testy_mcpants', 'testy@example.com', password='foo')
    
    def test_creation(self):
        # Start with a clean slate.
        self.assertEqual(FlatPage.objects.count(), 0)
        self.assertEqual(FlatPageSnapshot.objects.count(), 0)
        
        superflatpage = FlatPage.objects.create(
            title='My Test Page',
            content_format='rst',
            content='This is a sample flatpage.',
            last_modified_by=self.user
        )
        
        self.assertEqual(FlatPage.objects.count(), 1)
        
        # Check the auto-generated bits.
        latest_flatpage = FlatPage.objects.latest('created')
        self.assertEqual(latest_flatpage.slug, 'my-test-page')
        self.assertEqual(latest_flatpage.path, 'my-test-page')
        
        # Snapshots only get generated after the object exists.
        self.assertEqual(FlatPage.objects.count(), 1)
        self.assertEqual(FlatPageSnapshot.objects.count(), 1)
        latest_snapshot = FlatPageSnapshot.objects.latest('created')
        self.assertEqual(latest_snapshot.title, 'My Test Page')
        self.assertEqual(latest_snapshot.content_format, 'rst')
        self.assertEqual(latest_snapshot.content, 'This is a sample flatpage.')
        self.assertEqual(latest_snapshot.last_modified_by.username, 'testy_mcpants')
        self.assertEqual(latest_snapshot.message, u'Auto-saved')
        
        # Now update the content.
        superflatpage.content = 'This is a sample superflatpage.'
        superflatpage.save(message='Updated the content to be more correct.')
        
        self.assertEqual(FlatPage.objects.count(), 1)
        self.assertEqual(FlatPageSnapshot.objects.count(), 2)
        latest_snapshot = FlatPageSnapshot.objects.latest('created')
        self.assertEqual(latest_snapshot.title, 'My Test Page')
        self.assertEqual(latest_snapshot.content_format, 'rst')
        self.assertEqual(latest_snapshot.content, 'This is a sample superflatpage.')
        self.assertEqual(latest_snapshot.last_modified_by.username, 'testy_mcpants')
        self.assertEqual(latest_snapshot.message, u'Updated the content to be more correct.')
        
        # Now update the content again.
        superflatpage.title = 'More On My Test Page'
        superflatpage.save(message='Updated the title.')
        
        # Make sure the slug and the path don't change.
        self.assertEqual(FlatPage.objects.count(), 1)
        latest_flatpage = FlatPage.objects.latest('created')
        self.assertEqual(latest_flatpage.slug, 'my-test-page')
        self.assertEqual(latest_flatpage.path, 'my-test-page')
        
        # Examine the latest snapshot.
        self.assertEqual(FlatPageSnapshot.objects.count(), 3)
        latest_snapshot_2 = FlatPageSnapshot.objects.latest('created')
        self.assertNotEqual(latest_snapshot_2.id, latest_snapshot.id)
        self.assertEqual(latest_snapshot_2.title, u'More On My Test Page')
        self.assertEqual(latest_snapshot_2.content_format, 'rst')
        self.assertEqual(latest_snapshot_2.content, 'This is a sample superflatpage.')
        self.assertEqual(latest_snapshot_2.last_modified_by.username, 'testy_mcpants')
        self.assertEqual(latest_snapshot_2.message, 'Updated the title.')
        
        # Now a child.
        child_superflatpage = FlatPage.objects.create(
            title='Another Test Page',
            content_format='txt',
            content='Yet another test.',
            last_modified_by=self.user,
            parent=superflatpage
        )
        
        self.assertEqual(FlatPage.objects.count(), 2)
        latest_flatpage = FlatPage.objects.latest('created')
        self.assertEqual(latest_flatpage.slug, u'another-test-page')
        # Test path generation.
        self.assertEqual(latest_flatpage.path, u'my-test-page/another-test-page')
        self.assertEqual(latest_flatpage.parent.id, superflatpage.id)
        
        # Examine the latest snapshot.
        self.assertEqual(FlatPageSnapshot.objects.count(), 4)
        latest_snapshot_2 = FlatPageSnapshot.objects.latest('created')
        self.assertNotEqual(latest_snapshot_2.id, latest_snapshot.id)
        self.assertEqual(latest_snapshot_2.title, u'Another Test Page')
        self.assertEqual(latest_snapshot_2.content_format, 'txt')
        self.assertEqual(latest_snapshot_2.content, 'Yet another test.')
        self.assertEqual(latest_snapshot_2.last_modified_by.username, 'testy_mcpants')
        self.assertEqual(latest_snapshot_2.message, u'Auto-saved')


class FlatPageViewsTestCase(TestCase):
    urls = 'superflatpages.urls'
    
    def setUp(self):
        super(FlatPageViewsTestCase, self).setUp()
        self.user = User.objects.create_user('testy_mcpants', 'testy@example.com', password='foo')
        superflatpage = FlatPage.objects.create(
            title='My Test Page',
            content_format='rst',
            content='This is a sample flatpage.',
            last_modified_by=self.user
        )
        
        child_superflatpage = FlatPage.objects.create(
            title='Another Test Page',
            content_format='txt',
            content='Yet another test.',
            last_modified_by=self.user,
            custom_template='superflatpages/child.html',
            parent=superflatpage
        )
    
    def test_nonexistent(self):
        resp = self.client.get('/not-found/')
        self.assertEqual(resp.status_code, 404)
    
    def test_detail(self):
        resp = self.client.get('/my-test-page/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['flatpage'].title, u'My Test Page')
        self.assertEqual(resp.template[0].name, 'superflatpages/detail.html')
        
        resp = self.client.get('/my-test-page/another-test-page/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['flatpage'].title, u'Another Test Page')
        self.assertEqual(resp.template[0].name, 'superflatpages/child.html')
