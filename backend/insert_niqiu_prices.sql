-- ============================================================
-- 泥鳅价格数据 INSERT 脚本
-- 数据来源：中山水产品流通价格信息（微信公众号）
-- 时间范围：2026-02-12 至 2026-05-14
-- fish_id=2 (泥鳅), market_id=104, price_type='pond'
-- 规格: 20条（每斤约20条的泥鳅）
-- 价格单位：元/斤（直接存入，不转换）
-- 共 13 条记录
-- ============================================================

-- 先删除已有数据，保证脚本可重复执行
DELETE FROM prices WHERE fish_id = 2 AND market_id = 104 AND ts BETWEEN '2026-02-12' AND '2026-05-14' AND source_url LIKE 'https://mp.weixin.qq.com/s/%';

-- 第1篇: https://mp.weixin.qq.com/s/nmEy4RtMDsPTkvlybZRhAQ
-- 日期: 2026-02-12, 规格: 20条, 价格: 7.4元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 7.4000, 'CNY', 'kg', '2026-02-12', 'pond', 'https://mp.weixin.qq.com/s/nmEy4RtMDsPTkvlybZRhAQ', NOW());

-- 第2篇: https://mp.weixin.qq.com/s/ToaWMQKRDp8LFNncJUK7Ng
-- 日期: 2026-02-15, 规格: 20条, 价格: 7.4元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 7.4000, 'CNY', 'kg', '2026-02-15', 'pond', 'https://mp.weixin.qq.com/s/ToaWMQKRDp8LFNncJUK7Ng', NOW());

-- 第3篇: https://mp.weixin.qq.com/s/S0T4IFvvzBRDPiRixV4UEw
-- 日期: 2026-02-26, 规格: 20条, 价格: 6.0元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 6.0000, 'CNY', 'kg', '2026-02-26', 'pond', 'https://mp.weixin.qq.com/s/S0T4IFvvzBRDPiRixV4UEw', NOW());

-- 第4篇: https://mp.weixin.qq.com/s/upW0NXIFjW5gJQWjL13ckw
-- 日期: 2026-03-05, 规格: 20条, 价格: 4.8元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.8000, 'CNY', 'kg', '2026-03-05', 'pond', 'https://mp.weixin.qq.com/s/upW0NXIFjW5gJQWjL13ckw', NOW());

-- 第5篇: https://mp.weixin.qq.com/s/pyk8lyeY8lLSjXR4Yq02Zw
-- 日期: 2026-03-12, 规格: 20条, 价格: 5.0元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 5.0000, 'CNY', 'kg', '2026-03-12', 'pond', 'https://mp.weixin.qq.com/s/pyk8lyeY8lLSjXR4Yq02Zw', NOW());

-- 第6篇: https://mp.weixin.qq.com/s/dm2mEvOZObrO9Gmtwsttkw
-- 日期: 2026-03-19, 规格: 20条, 价格: 4.3元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.3000, 'CNY', 'kg', '2026-03-19', 'pond', 'https://mp.weixin.qq.com/s/dm2mEvOZObrO9Gmtwsttkw', NOW());

-- 第7篇: https://mp.weixin.qq.com/s/fWbly4vo5o7geZ4-0Z9jmQ
-- 日期: 2026-03-26, 规格: 20条, 价格: 4.6元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.6000, 'CNY', 'kg', '2026-03-26', 'pond', 'https://mp.weixin.qq.com/s/fWbly4vo5o7geZ4-0Z9jmQ', NOW());

-- 第8篇: https://mp.weixin.qq.com/s/AI7dEVrP0fkm9q7txZ9-QA
-- 日期: 2026-04-02, 规格: 20条, 价格: 5.0元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 5.0000, 'CNY', 'kg', '2026-04-02', 'pond', 'https://mp.weixin.qq.com/s/AI7dEVrP0fkm9q7txZ9-QA', NOW());

-- 第9篇: https://mp.weixin.qq.com/s/yjw1NO3nGVYE17OaqkXFmw
-- 日期: 2026-04-16, 规格: 20条, 价格: 4.5-4.7元/斤, 取中值4.6元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.6000, 'CNY', 'kg', '2026-04-16', 'pond', 'https://mp.weixin.qq.com/s/yjw1NO3nGVYE17OaqkXFmw', NOW());

-- 第10篇: https://mp.weixin.qq.com/s/ULXLsNrrxUrRW58p1S8aHw
-- 日期: 2026-04-23, 规格: 20条, 价格: 4.3元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.3000, 'CNY', 'kg', '2026-04-23', 'pond', 'https://mp.weixin.qq.com/s/ULXLsNrrxUrRW58p1S8aHw', NOW());

-- 第11篇: https://mp.weixin.qq.com/s/axZLByLLWqmQlMLayOxNTw
-- 日期: 2026-04-30, 规格: 20条, 价格: 4.2元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 4.2000, 'CNY', 'kg', '2026-04-30', 'pond', 'https://mp.weixin.qq.com/s/axZLByLLWqmQlMLayOxNTw', NOW());

-- 第12篇: https://mp.weixin.qq.com/s/1WUCMo5JWAkGCF8wnRArMg
-- 日期: 2026-05-07, 规格: 20条, 价格: 5.5元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 5.5000, 'CNY', 'kg', '2026-05-07', 'pond', 'https://mp.weixin.qq.com/s/1WUCMo5JWAkGCF8wnRArMg', NOW());

-- 第13篇: https://mp.weixin.qq.com/s/6pHS2exAb89P-Lk6sUWLFA
-- 日期: 2026-05-14, 规格: 20条, 价格: 5.5元/斤
INSERT INTO prices (fish_id, market_id, price, currency, unit, ts, price_type, source_url, created_at)
VALUES (2, 104, 5.5000, 'CNY', 'kg', '2026-05-14', 'pond', 'https://mp.weixin.qq.com/s/6pHS2exAb89P-Lk6sUWLFA', NOW());
