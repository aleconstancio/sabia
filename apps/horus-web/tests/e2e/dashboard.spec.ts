import { test, expect } from '@playwright/test';

test('dashboard shows ESG scorecards', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.locator('text=Regions Monitored')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('text=Avg NDVI Health')).toBeVisible();
  await expect(page.locator('text=Active Alerts')).toBeVisible();
  await expect(page.locator('text=Avg Temperature')).toBeVisible();
});

test('dashboard shows portfolio grid or empty state', async ({ page }) => {
  await page.goto('/dashboard');
  const hasContent = await page.locator('text=No regions monitored').isVisible() 
    || await page.locator('[class*="profile"]').isVisible();
  expect(hasContent).toBeTruthy();
});
