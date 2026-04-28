-- FLAMES PIZZA — Revenue by Platform
-- Shows total revenue and row count per platform
-- across all 8 years of data (2018-2026)

SELECT platform, 
       COUNT(*) as total_rows,
       ROUND(SUM(gross_amount)::numeric, 2) as total_revenue
FROM daily_revenue
GROUP BY platform
ORDER BY total_revenue DESC;
