const { Lunar } = require('lunar-javascript');

// 测试农历转换
const lunar = Lunar.fromYmd(2026, 1, 13);
const solar = lunar.getSolar();
console.log('农历2026年正月十三 -> 公历:', solar.toString());

const lunar2 = Lunar.fromYmd(2026, 1, 30);
const solar2 = lunar2.getSolar();
console.log('农历2026年正月三十 -> 公历:', solar2.toString());

const lunar3 = Lunar.fromYmd(2026, 2, 1);
const solar3 = lunar3.getSolar();
console.log('农历2026年二月初一 -> 公历:', solar3.toString());
