import { expect, test } from "@playwright/test";

// Helper function to login
async function login(page: any) {
  await page.goto("/login");
  await page.getByPlaceholder("Enter username").fill("user");
  await page.getByPlaceholder("Enter password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL("/board");
}

test.describe("Authentication", () => {
  test("shows login page by default", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
    await expect(page.getByText("Sign in to manage your projects")).toBeVisible();
  });

  test("logs in with correct credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("Enter username").fill("user");
    await page.getByPlaceholder("Enter password").fill("password");
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL("/board");
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  });

  test("shows error with wrong credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("Enter username").fill("wrong");
    await page.getByPlaceholder("Enter password").fill("wrong");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });

  test("logs out successfully", async ({ page }) => {
    await login(page);
    await page.getByRole("button", { name: /log out/i }).click();
    await page.waitForURL("/login");
    await expect(page.getByText("Sign in to manage your projects")).toBeVisible();
  });

  test("redirects to login when accessing board without auth", async ({ page }) => {
    await page.goto("/board");
    await page.waitForURL("/login");
    await expect(page.getByText("Sign in to manage your projects")).toBeVisible();
  });
});

test.describe("Kanban Board", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test("loads the kanban board with data from backend", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
    // Check that cards from backend are loaded
    await expect(page.getByText("Align roadmap themes")).toBeVisible();
  });

  test("adds a card to a column and persists", async ({ page }) => {
    const firstColumn = page.locator('[data-testid^="column-"]').first();
    await firstColumn.getByRole("button", { name: /add a card/i }).click();
    await firstColumn.getByPlaceholder("Card title").fill("E2E Test Card");
    await firstColumn.getByPlaceholder("Details").fill("Added via e2e test.");
    await firstColumn.getByRole("button", { name: /add card/i }).click();
    await expect(firstColumn.getByText("E2E Test Card")).toBeVisible();

    // Refresh page to verify persistence
    await page.reload();
    await expect(firstColumn.getByText("E2E Test Card")).toBeVisible();
  });

  test("deletes a card and persists", async ({ page }) => {
    // First add a card to delete
    const firstColumn = page.locator('[data-testid^="column-"]').first();
    await firstColumn.getByRole("button", { name: /add a card/i }).click();
    await firstColumn.getByPlaceholder("Card title").fill("Card to Delete");
    await firstColumn.getByPlaceholder("Details").fill("Will be deleted.");
    await firstColumn.getByRole("button", { name: /add card/i }).click();
    await expect(firstColumn.getByText("Card to Delete")).toBeVisible();

    // Delete the card
    const card = firstColumn.getByText("Card to Delete").locator("..");
    await card.hover();
    await card.getByRole("button", { name: /delete/i }).click();
    await expect(firstColumn.getByText("Card to Delete")).not.toBeVisible();

    // Refresh to verify persistence
    await page.reload();
    await expect(firstColumn.getByText("Card to Delete")).not.toBeVisible();
  });

  test("moves a card between columns and persists", async ({ page }) => {
    const card = page.getByTestId("card-card-1");
    const targetColumn = page.getByTestId("column-col-review");
    const cardBox = await card.boundingBox();
    const columnBox = await targetColumn.boundingBox();
    if (!cardBox || !columnBox) {
      throw new Error("Unable to resolve drag coordinates.");
    }

    await page.mouse.move(
      cardBox.x + cardBox.width / 2,
      cardBox.y + cardBox.height / 2
    );
    await page.mouse.down();
    await page.mouse.move(
      columnBox.x + columnBox.width / 2,
      columnBox.y + 120,
      { steps: 12 }
    );
    await page.mouse.up();
    await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();

    // Refresh to verify persistence
    await page.reload();
    await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
  });

  test("renames a column and persists", async ({ page }) => {
    const firstColumn = page.locator('[data-testid^="column-"]').first();
    const columnTitle = firstColumn.locator("h2");
    
    // Click to edit
    await columnTitle.click();
    const input = firstColumn.locator("input[type='text']");
    await input.fill("Renamed Column");
    await input.press("Enter");
    
    await expect(firstColumn.getByText("Renamed Column")).toBeVisible();

    // Refresh to verify persistence
    await page.reload();
    await expect(firstColumn.getByText("Renamed Column")).toBeVisible();
  });

  test("maintains board state across page refresh", async ({ page }) => {
    // Add a card
    const firstColumn = page.locator('[data-testid^="column-"]').first();
    await firstColumn.getByRole("button", { name: /add a card/i }).click();
    await firstColumn.getByPlaceholder("Card title").fill("Persistence Test");
    await firstColumn.getByPlaceholder("Details").fill("Testing persistence.");
    await firstColumn.getByRole("button", { name: /add card/i }).click();
    await expect(firstColumn.getByText("Persistence Test")).toBeVisible();

    // Refresh page
    await page.reload();

    // Verify card is still there
    await expect(firstColumn.getByText("Persistence Test")).toBeVisible();
  });
});
