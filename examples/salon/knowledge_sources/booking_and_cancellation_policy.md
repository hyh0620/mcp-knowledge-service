# 预约与改约取消规则 Booking and Cancellation Policy

Version: 2026.07
Updated: 2026-07-07

## 概述

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 概述.

本文档用于回答预约规则、改约、取消、迟到和临时无法到店的咨询。预约是否创建成功仍由主项目后端确定性处理，包括服务目录、营业时间、发型师排班和冲突校验。

知识库可以解释政策，但不能覆盖业务数据库中的实际预约状态。

## 预约规则

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 预约规则.

预约成功后，请按预约时间到店。若预计迟到超过 15 分钟，建议提前联系门店，避免影响后续顾客。

用户可以指定发型师，也可以让系统根据服务类型、风格偏好、预算、可预约时间和发型师专长推荐。指定发型师并不等于一定预约成功，最终仍要通过发型师排班和冲突校验。

## 改约规则

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 改约规则.

改约建议至少提前 2 小时联系门店或在系统中重新选择时间。染发、烫发等长时服务建议更早沟通，因为它们会占用更长连续档期。

改约时需要重新校验服务时长、营业时间、发型师可用性和冲突情况。原发型师不一定在新时间可约，系统可能推荐相近专长的发型师。

## 取消规则

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 取消规则.

取消预约建议至少提前 2 小时处理。临时不能到店时，应尽早联系门店，方便释放发型师档期给其他顾客。

频繁临时取消或爽约可能影响后续高峰时段预约安排。此规则用于门店运营提醒，不应由 LLM 自动惩罚用户或更改账户状态。

## 迟到和未到店

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 迟到和未到店.

迟到超过 15 分钟时，门店会根据当天排班判断是否保留原预约。如果后续已有其他预约，门店可能建议改约或调整服务项目。

如果顾客没有提前说明且未到店，门店会记录该次未到店情况。是否影响后续安排，由门店规则和人工沟通决定。

## 政策例外

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 政策例外.

遇到极端天气、交通中断、门店设备维护、发型师突发不可用等情况，门店会优先协助改约或推荐其他可预约发型师。

如果是染发或烫发服务，且顾客已经到店完成部分沟通或准备流程，改约和取消处理需要结合现场情况人工确认。

## 常见问答

Source document: booking_and_cancellation_policy. Version: 2026.07. Updated: 2026-07-07. Section: 常见问答.

问：临时不能到店，改约规则是什么？
答：建议至少提前 2 小时联系门店或重新选择时间，长时服务建议更早沟通。

问：取消预约最晚提前多久？
答：建议至少提前 2 小时取消，越早处理越便于释放档期。

问：指定发型师后一定能约上吗？
答：不一定，仍要通过发型师排班和时段冲突校验。
