import { test, expect } from '@playwright/test';

test('map page loads with Leaflet container', async ({ page }) => {
  await page.goto('/map');
  await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: 15000 });
});

test('map page shows search sidebar', async ({ page }) => {
  await page.goto('/map');
  await expect(page.locator('text=Buscar imagens')).toBeVisible({ timeout: 10000 });
});
