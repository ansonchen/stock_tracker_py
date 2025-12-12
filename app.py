import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, time
import data_manager

st.set_page_config(page_title="每日A股交易记录", layout="wide")

st.title("📈 每日A股交易记录")

# --- 导航与路由 ---

def navigate_to(page, **kwargs):
    st.query_params["page"] = page
    for key, value in kwargs.items():
        st.query_params[key] = value
    st.rerun()

def show_create():
    st.header("➕ 新增交易")
    
    def update_name_add():
        code = st.session_state.code_input_add
        if code:
            name = data_manager.get_stock_name(code)
            st.session_state.stock_name_add = name

    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("股票代码", key="code_input_add", on_change=update_name_add)
    with col2:
        name = st.text_input("股票名称", key="stock_name_add", disabled=True)

    with st.form("add_trade_form"):
        col3, col4 = st.columns(2)
        with col3:

            b_date_col, b_time_col = st.columns(2)
            with b_date_col:
                buy_date = st.date_input("买入日期", value=date.today())
            with b_time_col:
                buy_time = st.time_input("买入时间", value=time(9, 30), step=60)
            buy_datetime = datetime.combine(buy_date, buy_time)
        with col4:
            buy_price = st.number_input("买入价格", min_value=0.0, format="%.2f")

        col5, col6 = st.columns(2)
        with col5:
            buy_qty = st.number_input("买入数量", min_value=100, step=100)
        with col6:
            position = st.multiselect("位置", ["A区", "B区", "股价平台", "前强势能量颈高处", "前异动区区域", "前异动区重要支撑位"])

        col7, col8 = st.columns(2)
        with col7:
            strategy = st.multiselect("战法", ["星线", "单日洗盘", "缺口"])
        with col8:
            operation = st.radio("操作", ["追涨", "低吸"], horizontal=True)
        verification = st.radio("两点印证", ["是", "否"], horizontal=True)
        st.markdown("---")
        st.subheader("卖出信息 (可选)")
        col9, col10 = st.columns(2)
        with col9:

            s_date_col, s_time_col = st.columns(2)
            with s_date_col:
                sell_date = st.date_input("卖出日期", value=None)
            with s_time_col:
                sell_time = st.time_input("卖出时间", value=time(9, 30), step=60)

            sell_datetime = None
            if sell_date:
                sell_datetime = datetime.combine(sell_date, sell_time) if sell_time else datetime.combine(sell_date, time(0, 0))
        with col10:
            sell_price = st.number_input("卖出价格", min_value=0.0, format="%.2f")
        
        sell_qty = st.number_input("卖出数量", min_value=0, step=100)

        
        remarks = st.text_area("备注")

        c1, c2 = st.columns([1, 1])
        with c1:
            submitted = st.form_submit_button("💾 保存记录", type="primary")
        with c2:
            cancelled = st.form_submit_button("❌ 取消")

        if submitted:
            if not code:
                st.error("请输入股票代码")
            else:
                trade_data = {
                    "代码": code,
                    "名称": st.session_state.stock_name_add,
                    "买入日期": buy_datetime,
                    "买入价格": buy_price,
                    "买入数量": buy_qty,
                    "卖出日期": sell_datetime,
                    "卖出价格": sell_price if sell_price > 0 else None,
                    "卖出数量": sell_qty if sell_qty > 0 else None,
                    "位置": ", ".join(position),
                    "战法": ", ".join(strategy),
                    "操作": operation,
                    "两点印证": verification,
                    "备注": remarks
                }
                if data_manager.save_trade(trade_data):
                    st.success("交易记录已保存!")
                    navigate_to("home")
        
        if cancelled:
            navigate_to("home")

def show_edit(trade_id):
    st.header("📝 编辑交易")
    
    df = data_manager.load_data()
    if df.empty or "ID" not in df.columns:
        st.error("数据加载失败或无数据")
        if st.button("返回首页"):
            navigate_to("home")
        return

    row_data = df[df["ID"] == trade_id]
    if row_data.empty:
        st.error("未找到该交易记录")
        if st.button("返回首页"):
            navigate_to("home")
        return
    
    selected_row = row_data.iloc[0]

    with st.form("edit_trade_form"):
        # 预填充值
        ec1, ec2 = st.columns(2)
        with ec1:
            e_code = st.text_input("股票代码", value=selected_row["代码"])
        with ec2:
            e_name = st.text_input("股票名称", value=selected_row["名称"])

        ec3, ec4 = st.columns(2)
        with ec3:

            val_buy_date = selected_row["买入日期"]
            val_buy_time = time(9, 30)

            if isinstance(val_buy_date, pd.Timestamp):
                val_buy_time = val_buy_date.time()
                val_buy_date = val_buy_date.date()
            elif isinstance(val_buy_date, datetime):
                val_buy_time = val_buy_date.time()
                val_buy_date = val_buy_date.date()
            elif isinstance(val_buy_date, str):
                try:
                     dt = datetime.strptime(val_buy_date, "%Y-%m-%d %H:%M:%S")
                     val_buy_date = dt.date()
                     val_buy_time = dt.time()
                except:
                     pass

            eb_date_col, eb_time_col = st.columns(2)
            with eb_date_col:
                e_buy_date = st.date_input("买入日期", value=val_buy_date)
            with eb_time_col:
                e_buy_time = st.time_input("买入时间", value=val_buy_time, step=60)

            e_buy_datetime = datetime.combine(e_buy_date, e_buy_time)
        with ec4:
            e_buy_price = st.number_input("买入价格", value=float(selected_row["买入价格"]), min_value=0.0, format="%.2f")

        ec5, ec6 = st.columns(2)
        with ec5:
            e_buy_qty = st.number_input("买入数量", value=int(selected_row["买入数量"]), min_value=100, step=100)
        with ec6:
            pos_val = selected_row["位置"]
            pos_opts = ["A区", "B区", "股价平台", "前强势能量颈高处", "前异动区区域", "前异动区重要支撑位"]
            
            default_pos = []
            if isinstance(pos_val, str) and pos_val:
                default_pos = pos_val.split(", ")
                # Filter out invalid options just in case
                default_pos = [p for p in default_pos if p in pos_opts]
            
            e_position = st.multiselect("位置", pos_opts, default=default_pos)

        ec7, ec8 = st.columns(2)
        with ec7:
            strat_val = selected_row["战法"]
            default_strategies = strat_val.split(", ") if isinstance(strat_val, str) and strat_val else []
            valid_strategies = ["星线", "单日洗盘", "缺口"]
            default_strategies = [s for s in default_strategies if s in valid_strategies]
            e_strategy = st.multiselect("战法", valid_strategies, default=default_strategies)
        with ec8:
            op_val = selected_row["操作"]
            op_opts = ["追涨", "低吸"]
            op_idx = op_opts.index(op_val) if op_val in op_opts else 0
            e_operation = st.radio("操作", op_opts, index=op_idx, horizontal=True)
        ver_val = selected_row["两点印证"]
        ver_opts = ["是", "否"]
        ver_idx = ver_opts.index(ver_val) if ver_val in ver_opts else 0
        e_verification = st.radio("两点印证", ver_opts, index=ver_idx, horizontal=True)
        st.markdown("---")
        ec9, ec10 = st.columns(2)
        with ec9:

            val_sell_date = selected_row["卖出日期"]
            val_sell_time = time(9, 30)

            if pd.isna(val_sell_date):
                val_sell_date = date.today()
            elif isinstance(val_sell_date, pd.Timestamp):
                val_sell_time = val_sell_date.time()
                val_sell_date = val_sell_date.date()
            elif isinstance(val_sell_date, datetime):
                val_sell_time = val_sell_date.time()
                val_sell_date = val_sell_date.date()
            elif isinstance(val_sell_date, str):
                 try:
                     dt = datetime.strptime(val_sell_date, "%Y-%m-%d %H:%M:%S")
                     val_sell_date = dt.date()
                     val_sell_time = dt.time()
                 except:
                     pass

            es_date_col, es_time_col = st.columns(2)
            with es_date_col:
                e_sell_date = st.date_input("卖出日期", value=val_sell_date)
            with es_time_col:
                e_sell_time = st.time_input("卖出时间", value=val_sell_time, step=60)

            e_sell_datetime = datetime.combine(e_sell_date, e_sell_time)
        with ec10:
            e_sell_price = st.number_input("卖出价格", value=float(selected_row["卖出价格"]) if pd.notna(selected_row["卖出价格"]) else 0.0, min_value=0.0, format="%.2f")
        
        e_sell_qty = st.number_input("卖出数量", value=int(selected_row["卖出数量"]) if pd.notna(selected_row["卖出数量"]) else 0, min_value=0, step=100)

        
        e_remarks = st.text_area("备注", value=selected_row["备注"] if pd.notna(selected_row["备注"]) else "")

        col_update, col_cancel = st.columns([1, 1])
        with col_update:
            update_submitted = st.form_submit_button("💾 保存修改", type="primary")
        with col_cancel:
            cancel_submitted = st.form_submit_button("❌ 取消")

        if update_submitted:
            updated_data = {
                "代码": e_code,
                "名称": e_name,
                "买入日期": e_buy_datetime,
                "买入价格": e_buy_price,
                "买入数量": e_buy_qty,
                "卖出日期": e_sell_datetime,
                "卖出价格": e_sell_price if e_sell_price > 0 else None,
                "卖出数量": e_sell_qty if e_sell_qty > 0 else None,
                "位置": ", ".join(e_position),
                "战法": ", ".join(e_strategy),
                "操作": e_operation,
                "两点印证": e_verification,
                "备注": e_remarks
            }
            if data_manager.update_trade(trade_id, updated_data):
                st.success("记录已更新!")
                navigate_to("home")
        
        if cancel_submitted:
            navigate_to("home")

    # 在表单外部删除，以避免嵌套表单问题或为了清晰起见
    st.markdown("---")
    if st.button("🗑️ 删除记录", type="secondary"):
        st.session_state.confirm_delete = True

    if st.session_state.get("confirm_delete", False):
        st.warning("确定要删除这条记录吗？此操作不可恢复。")
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            if st.button("✅ 确认删除", type="primary"):
                if data_manager.delete_trade(trade_id):
                    st.success("记录已删除!")
                    st.session_state.confirm_delete = False
                    navigate_to("home")
        with col_d2:
            if st.button("❌ 取消删除"):
                st.session_state.confirm_delete = False
                st.rerun()

def show_home():
    if st.button("➕ 新增交易", type="primary"):
        navigate_to("create")

    # 加载数据
    df = data_manager.load_data()
    
    # 调试：打印到控制台
    print(f"Loaded {len(df)} rows")

    if not df.empty:
        # 确保日期列为 datetime 类型
        df["买入日期"] = pd.to_datetime(df["买入日期"])
        df["卖出日期"] = pd.to_datetime(df["卖出日期"])

        # --- 统计概览 ---
        st.header("📊 统计概览")
        
        closed_trades = df.dropna(subset=["盈亏"])
        
        if not closed_trades.empty:
            total_pnl = closed_trades["盈亏"].sum()
            win_rate = (closed_trades[closed_trades["盈亏"] > 0].shape[0] / closed_trades.shape[0]) * 100
            
            m1, m2, m3 = st.columns(3)
            m1.metric("总盈亏", f"{total_pnl:.2f}")
            m2.metric("交易笔数", closed_trades.shape[0])
            m3.metric("胜率", f"{win_rate:.1f}%")

            tab1, tab2 = st.tabs(["每日盈亏", "累计盈亏"])
            
            with tab1:
                # 仅按日期部分分组
                daily_pnl = closed_trades.groupby(closed_trades["卖出日期"].dt.date)["盈亏"].sum().reset_index()
                # 将列名重命名回“卖出日期”以保持与图表代码的一致性，或者调整图表代码
                daily_pnl.columns = ["卖出日期", "盈亏"]
                fig_daily = px.bar(daily_pnl, x="卖出日期", y="盈亏", title="每日盈亏", color="盈亏", 
                                   color_continuous_scale=["green", "red"])
                fig_daily.update_traces(marker_color=daily_pnl["盈亏"].apply(lambda x: 'red' if x >= 0 else 'green'))
                st.plotly_chart(fig_daily, use_container_width=True)

            with tab2:
                closed_trades = closed_trades.sort_values("卖出日期")
                closed_trades["累计盈亏"] = closed_trades["盈亏"].cumsum()
                fig_cum = px.line(closed_trades, x="卖出日期", y="累计盈亏", title="资金曲线", markers=True)
                fig_cum.update_traces(line_color='red')
                st.plotly_chart(fig_cum, use_container_width=True)

        else:
            st.info("暂无已平仓交易数据，无法计算盈亏统计。")

        # --- 数据表格 ---
        st.header("📋 交易明细")
        st.caption("点击表格行以编辑记录")
        
        
        event = st.dataframe(
            df,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={"ID": None}
        )

        if event.selection.rows:
            selected_index = event.selection.rows[0]
            selected_row = df.iloc[selected_index]
            trade_id = selected_row["ID"]
            navigate_to("edit", id=trade_id)

    else:
        st.info("暂无数据，请点击上方 '➕ 新增交易' 添加记录。")

# --- 主路由 ---
def main():
    # 处理查询参数
    params = st.query_params
    page = params.get("page", "home")

    if page == "create":
        show_create()
    elif page == "edit":
        trade_id = params.get("id")
        if trade_id:
            show_edit(trade_id)
        else:
            st.error("缺少交易ID")
            if st.button("返回首页"):
                navigate_to("home")
    else:
        show_home()

if __name__ == "__main__":
    main()
