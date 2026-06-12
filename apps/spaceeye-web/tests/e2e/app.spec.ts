import { test, expect } from '@playwright/test';

test('app loads and redirects to dashboard', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/dashboard/);
});

test('dashboard page renders scorecards', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.locator('text=Regions Monitored')).toBeVisible({ timeout: 10000 });
});

test('navigation to map page works', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('a[href="/map"]');
  await expect(page).toHaveURL(/\/map/);
});
