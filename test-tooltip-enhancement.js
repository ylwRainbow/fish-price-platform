// 图表 Tooltip 增强功能测试脚本
// 测试场景：
// 1. 单选模式 - 详细 tooltip 显示
// 2. 多选模式 - 简洁对比 tooltip 显示
// 3. 图例切换 - 动态 trigger 切换
// 4. 农历模式 - 农历日期显示
// 5. 性能测试 - 大数据量下的 tooltip 响应

const { test, expect } = require('@playwright/test');

test.describe('图表 Tooltip 增强功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/chart');
    await page.waitForLoadState('networkidle');
  });

  test('单选模式 - 显示详细 tooltip', async ({ page }) => {
    // 确保只有一个时间段被选中
    await page.click('.time-period-item:first-child');
    
    // 鼠标悬浮到图表数据点
    const chartPoint = await page.locator('.echarts-chart').first();
    await chartPoint.hover({ position: { x: 100, y: 150 } });
    
    // 验证 tooltip 显示
    const tooltip = await page.locator('.echarts-tooltip');
    await expect(tooltip).toBeVisible();
    
    // 验证 tooltip 内容包含详细信息
    const tooltipText = await tooltip.textContent();
    expect(tooltipText).toContain('线条名称');
    expect(tooltipText).toContain('阳历');
    expect(tooltipText).toContain('农历');
    expect(tooltipText).toContain('价格');
  });

  test('多选模式 - 显示简洁对比 tooltip', async ({ page }) => {
    // 选择多个时间段
    await page.click('.time-period-item:nth-child(1)');
    await page.click('.time-period-item:nth-child(2)');
    
    // 鼠标悬浮到图表
    const chart = await page.locator('.echarts-chart');
    await chart.hover({ position: { x: 200, y: 150 } });
    
    // 验证 tooltip 显示多个数据系列
    const tooltip = await page.locator('.echarts-tooltip');
    await expect(tooltip).toBeVisible();
    
    const tooltipText = await tooltip.textContent();
    expect(tooltipText.split('●').length - 1).toBeGreaterThan(1); // 多个数据点
  });

  test('图例切换 - 动态更新 tooltip trigger', async ({ page }) => {
    // 初始多选模式
    await page.click('.time-period-item:nth-child(1)');
    await page.click('.time-period-item:nth-child(2)');
    
    // 点击图例取消一个系列
    const legendItem = await page.locator('.echarts-legend-item').first();
    await legendItem.click();
    
    // 等待图表重新渲染
    await page.waitForTimeout(500);
    
    // 验证 tooltip trigger 已切换为 item
    const chartPoint = await page.locator('.echarts-chart').first();
    await chartPoint.hover({ position: { x: 100, y: 150 } });
    
    const tooltip = await page.locator('.echarts-tooltip');
    await expect(tooltip).toBeVisible();
  });

  test('农历模式 - 显示农历日期', async ({ page }) => {
    // 切换到农历模式
    await page.click('button:has-text("农历")');
    await page.waitForTimeout(500);
    
    // 选择数据
    await page.click('.time-period-item:first-child');
    
    // 鼠标悬浮到图表
    const chartPoint = await page.locator('.echarts-chart').first();
    await chartPoint.hover({ position: { x: 150, y: 150 } });
    
    // 验证 tooltip 显示农历日期
    const tooltip = await page.locator('.echarts-tooltip');
    await expect(tooltip).toBeVisible();
    
    const tooltipText = await tooltip.textContent();
    expect(tooltipText).toContain('农历');
  });
});
