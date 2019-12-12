# damai_crawler
简单易用的python-selenium大麦网抢票脚本，抢票完成之后还可以通过邮件通知进行付款操作。因为大麦网登录模块进行了人机检测，一直都过不了检测，所以被迫只能使用qq进行登录操作。

只需要修改配置的json文件，即可进行抢票操作

## 使用说明
1、最最最重要的，请先配置好selenium和对应的WebDriver

2、配置文件格式如下：
```
{
  // 开始购票的时间
  "buy_time": "2019-12-11 15:52",
  
  // 如果需要抢票完成后邮件通知，可配置下面三个邮箱信息
  // 发件host地址，下面是qq邮箱的
  "mail_host": "smtp.qq.com",
  
  // 邮箱账号
  "mail_user": "12345678@qq.com",
  
  // 发件密码，不是登录密码（在邮箱中开启host之后可见）
  "mail_pass": "asdjahsdjkhjkas",
  
  // 购票数量
  "buy_num": 2,
  
  // 用户信息，可以同时使用多个账号
  "users": [
    {
      // 账号所绑定的qq号
      "qq_num": "1323123124",
      
      // qq密码
      "qq_pass": "ADADSASDADA",
      
      // 大麦网的昵称
      "username": "麦子sdasd",
      
      // 抢票地址
      "url": "https://detail.damai.cn/item.htm?spm=a2oeg.home.card_0.ditem_0.591b23e1Vcorqm&id=609134671437",
      
      // 如果抢票地址有多个城市，需要指定购买哪个城市，格式：成都（不要带省、市、县，），若只有一个城市则为null
      "city": null,
      
      // 如果抢票地址有多个场次，需要指定购买哪个日期，格式：2019-11-11。若只有一个场次则为null
      "date": null,
      
      // 购票价格的列表，从上到下优先级从高到低
      "price_list": [
        680,
        780
      ]
    },
    {
      "qq_num": "可以多个账号进行抢票",
      "qq_pass": "如上",
      "username": "如上",
      "url": "如上",
      "city": "成都",
      "date": "2012-12-12",
      "price_list": [
        242,
        2412
      ]
    }
  ]
}
```
3、如果在使用过程中有任何问题，欢迎提issue

