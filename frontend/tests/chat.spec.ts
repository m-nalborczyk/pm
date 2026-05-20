import { test, expect } from "@playwright/test";

test.describe("AI Chat", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.fill('input[name="username"]', "user");
    await page.fill('input[name="password"]', "password");
    await page.click('button[type="submit"]');
    await page.waitForURL("/board");
  });

  test("opens and closes chat sidebar", async ({ page }) => {
    const chatButton = page.getByTestId("chat-toggle-button");
    await expect(chatButton).toBeVisible();

    await chatButton.click();

    const sidebar = page.getByTestId("chat-sidebar");
    await expect(sidebar).toBeVisible();
    await expect(sidebar).not.toHaveClass(/translate-x-full/);

    const closeButton = page.getByTestId("chat-close-button");
    await closeButton.click();

    await expect(sidebar).toHaveClass(/translate-x-full/);
  });

  test("closes chat when clicking backdrop", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const sidebar = page.getByTestId("chat-sidebar");
    await expect(sidebar).toBeVisible();

    await page.getByTestId("chat-backdrop").click();

    await expect(sidebar).toHaveClass(/translate-x-full/);
  });

  test("displays empty state initially", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    await expect(page.getByText("Start a conversation")).toBeVisible();
  });

  test("sends message and receives response", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("What cards are in the Backlog?");
    await sendButton.click();

    await expect(page.getByText("What cards are in the Backlog?")).toBeVisible();

    await expect(
      page.getByTestId("chat-message-assistant")
    ).toBeVisible({ timeout: 10000 });
  });

  test("AI can add a card", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Add a card called 'Test Card' to Backlog");
    await sendButton.click();

    await expect(
      page.getByTestId("chat-message-assistant")
    ).toBeVisible({ timeout: 10000 });

    await page.getByTestId("chat-close-button").click();

    await expect(page.getByText("Test Card")).toBeVisible({ timeout: 5000 });
  });

  test("AI can move a card", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Add a card called 'Move Test' to Backlog");
    await sendButton.click();
    await page.waitForTimeout(2000);

    await input.fill("Move 'Move Test' to In Progress");
    await sendButton.click();

    await expect(
      page.getByTestId("chat-message-assistant")
    ).toBeVisible({ timeout: 10000 });

    await page.getByTestId("chat-close-button").click();

    const progressColumn = page.locator('[data-column-id="col-progress"]');
    await expect(progressColumn.getByText("Move Test")).toBeVisible({
      timeout: 5000,
    });
  });

  test("conversation history is maintained", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Hello");
    await sendButton.click();

    await expect(page.getByText("Hello")).toBeVisible();

    await page.waitForTimeout(1000);

    await input.fill("How are you?");
    await sendButton.click();

    await expect(page.getByText("Hello")).toBeVisible();
    await expect(page.getByText("How are you?")).toBeVisible();
  });

  test("shows loading state while waiting for response", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Test message");
    await sendButton.click();

    const button = page.getByTestId("chat-send-button");
    await expect(button).toBeDisabled();
  });

  test("reopening chat preserves conversation", async ({ page }) => {
    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Test message");
    await sendButton.click();

    await expect(page.getByText("Test message")).toBeVisible();

    await page.getByTestId("chat-close-button").click();
    await page.getByTestId("chat-toggle-button").click();

    await expect(page.getByText("Test message")).toBeVisible();
  });

  test("handles errors gracefully", async ({ page }) => {
    await page.route("**/api/ai/chat", (route) => {
      route.abort("failed");
    });

    await page.getByTestId("chat-toggle-button").click();

    const input = page.getByTestId("chat-input");
    const sendButton = page.getByTestId("chat-send-button");

    await input.fill("Test");
    await sendButton.click();

    await expect(page.getByText(/error/i)).toBeVisible({ timeout: 5000 });
  });
});

// Made with Bob
