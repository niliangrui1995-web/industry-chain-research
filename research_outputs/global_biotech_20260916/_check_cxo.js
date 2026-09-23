
var c1 = echarts.init(document.getElementById('chart1'));
c1.setOption({
  tooltip: { trigger: 'axis' },
  legend: { data: ['新签订单同比(%)', '年初至今涨幅(%)'] },
  grid: { left: 60, right: 60, top: 40, bottom: 40 },
  xAxis: { type: 'category', data: ['美迪西', '益诺思', '昭衍新药', '泰格医药*', '药明康德'] },
  yAxis: [
    { type: 'value', name: '订单同比(%)' },
    { type: 'value', name: 'YTD涨幅(%)' }
  ],
  series: [
    { name: '新签订单同比(%)', type: 'bar', data: [104.7, 175.6, 98.0, 20.0, 40.0],
      itemStyle: { color: '#2471a3' }, label: { show: true, position: 'top', fontSize: 11 } },
    { name: '年初至今涨幅(%)', type: 'bar', yAxisIndex: 1, data: [75.5, 95.9, 21.8, -1.45, 76.3],
      itemStyle: { color: function(p){ return p.value >= 0 ? '#d63c3c' : '#0d8a4f'; } },
      label: { show: true, position: 'top', fontSize: 11 } }
  ]
});
