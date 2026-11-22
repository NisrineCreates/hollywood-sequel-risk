import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Page configuration
st.set_page_config(
    page_title="Hollywood Risk Analysis",
    page_icon="🎬",
    layout="wide"
)

# Data loading 
@st.cache_data
def load_data():
    df = pd.read_csv("data/movies_final.csv")
    def budget_tier(x):
        if x < 10_000_000: return "1. Low (<$10M)"
        elif x < 50_000_000: return "2. Mid ($10M-$50M)"
        elif x < 100_000_000: return "3. High ($50M-$100M)"
        else: return "4. Blockbuster ($100M+)"
    df["budget_tier"] = df["budget"].apply(budget_tier)

    # --- ADD THIS BLOCK HERE ---
    def get_derivative_category(row):
        if not row['is_derivative']:
            return "Original"
        
        categories = []
        if row['is_franchise']: categories.append("Franchise/Sequel")
        if row['is_adaptation']: categories.append("Adaptation")
        if row['is_remake']: categories.append("Remake")
        
        return " & ".join(categories)

    df['derivative_type'] = df.apply(get_derivative_category, axis=1)
    # ---------------------------

    return df

df = load_data()


# Sidebar filters
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Hollywood_Sign_%28Zuschnitt%29.jpg/1200px-Hollywood_Sign_%28Zuschnitt%29.jpg", use_column_width=True)
st.sidebar.header("Filter the Data")
max_year = int(df["release_year"].max())
year_range = st.sidebar.slider("Select Release Year Range", 1990, max_year, (1990, max_year))

selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=df["primary_genre"].unique(),
    default=df["primary_genre"].unique()
)

# Apply filters
filtered_df = df[
    (df["release_year"] >= year_range[0]) &
    (df["release_year"] <= year_range[1]) &
    (df["primary_genre"].isin(selected_genres))
]

# Header & Metrics
st.title("🎬 Hollywood Risk Analysis")
st.markdown("""
**Has Hollywood lost its creativity, or is it just managing risk?** 
An investigation into 30 years of box office data to understand why sequels, remakes, and adaptations dominate modern cinema.
""")

st.markdown('---')

#Calculate metrics
orig_fail = (filtered_df[~filtered_df["is_derivative"]]["roi"] < 1).mean() * 100
deriv_fail = (filtered_df[filtered_df["is_derivative"]]["roi"] < 1).mean() * 100
orig_med = filtered_df[~filtered_df["is_derivative"]]["roi"].median()
deriv_med = filtered_df[filtered_df["is_derivative"]]["roi"].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Original Failure Rate", f"{orig_fail:.1f}%", help="% of original films that lost money (ROI < 1)")
col2.metric("Derivative Failure Rate", f"{deriv_fail:.1f}%", f"{deriv_fail - orig_fail:.1f}% lower risk", delta_color="inverse")
col3.metric("Median ROI (Original)", f"{orig_med:.2f}x")
col4.metric("Median ROI (Derivative)", f"{deriv_med:.2f}x")

st.markdown("---")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 The Investigation", "📈 The Shift in Strategy", "💸 The Financial Risk", "🎭 Genres & Studios", "🗂️ The Data Catalog"])# TAB 1: TREND

with tab1:
    st.header("The Hollywood Risk Premium")
    st.markdown("### *Why original ideas are becoming a luxury item.*")
    
    st.image("https://images.unsplash.com/photo-1485846234645-a62644f84728?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80", use_column_width=True)
    st.caption("Photo by Jeremy Yap on Unsplash")
    
    st.markdown("""
    Every year, audiences and critics ask the same question: **Has Hollywood run out of original ideas?** 
    Look at the box office, and the evidence seems overwhelming. Franchises, reboots, and adaptations of books and video games dominate the cultural conversation. 
    
    But the data tells a more complex story. It's not a creativity crisis; **it's a mathematical one.** 
    
    #### The Methodology
    To investigate this, I analyzed 30 years of box office data (1990–2025) from The Movie Database (TMDB). I looked at the top-grossing films of each year, cross-referencing their budget, revenue, and critical data. 
    
    To determine if a film was a **"Derivative Work,"** I combined three data points:
    *   **Franchises:** Films belonging to an existing TMDB collection (sequels, prequels).
    *   **Adaptations:** Films tagged with keywords like *"based on novel,"* *"based on video game,"* or *"based on comic."*
    *   **Remakes:** Films tagged as *"remake"* or *"reboot."*
    
    #### The Financial Reality
    Original films are still being made. In fact, they still make up roughly **50%** of the top-grossing releases. But the economics of making them have drastically changed.
    
    My analysis revealed a stark reality: **Original films are twice as likely to lose money.** 
    
    *   **Originals:** Have a **34% failure rate** (returning less than their budget).
    *   **Derivatives:** Have only an **18% failure rate**.
    
    Why does this happen? Because of **The Mid-Budget Gap**. When a studio spends $30 million on an original idea, they are taking a massive risk; if it fails, it can sink a studio's quarter. But when they spend $150 million on a known IP (like a Marvel movie or a *Dune* adaptation), the built-in global audience practically guarantees a return. 
    
    #### The Shift in Strategy
    As a result, derivative works now dominate the box office. In 1990, sequels and adaptations took in roughly 60% of the total revenue. Today, they take in **nearly 90%**.
    
    This isn't because audiences hate original stories. It's because studios have concentrated their marketing budgets and release strategies on the safest possible bets. When a studio *does* take a risk on an original blockbuster (like Christopher Nolan's *Inception* or *Oppenheimer*), it is treated as an anomaly, not the standard.
    
    #### The Conclusion: The Self-Fulfilling Prophecy
    **Hollywood hasn't completely lost its creativity—but it may be on the way there.**

    The data shows the industry is currently optimizing for risk management, not innovation. However, this strategy may be a self-fulfilling prophecy. By starving mid-budget original films of funding and marketing, studios are training audiences to only show up for existing IP. 
    
    If the industry continues down this path, the "creativity crisis" might become a reality—not because writers and directors have run out of ideas, but because the next generation of original blockbusters will never get the green light.
    """)
    

# TAB 2: RISK
with tab2:
    st.header("The Rise of Derivative Works")
    st.markdown("Studios are increasingly relying on existing intellectual property (IP). The lines below show the 3-year rolling average of the percentage of top-grossing films that are derivatives.")
        
    yearly = filtered_df.groupby("release_year")[["is_derivative", "is_franchise", "is_adaptation"]].mean().mul(100).rolling(3).mean()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=yearly.index, y=yearly["is_derivative"], name="Total Derivative", line=dict(color="#ff4b4b", width=4)))
    fig1.add_trace(go.Scatter(x=yearly.index, y=yearly["is_franchise"], name="Franchises (Sequels)", line=dict(color="#00d4ff", dash="dot")))
    fig1.add_trace(go.Scatter(x=yearly.index, y=yearly["is_adaptation"], name="Adaptations (Books/Games)", line=dict(color="#ffa600", dash="dash")))
    fig1.update_layout(yaxis_title="% of Top-Grossing Films", xaxis_title="Release Year", hovermode="x unified", template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)
    
    

# TAB 3: GENRES & STUDIOS
with tab3:
    st.header("The Financial Reality: Risk vs. Reward")
    st.markdown("Why is Hollywood doing this? Because original ideas are incredibly risky. The boxplot below shows the distribution of Return on Investment (ROI). Notice how much lower the failure rate (ROI < 1) is for derivatives.")
    
    fig2 = px.box(filtered_df, x="is_derivative", y="log_roi", color="is_derivative",
                    labels={"is_derivative": "Is Derivative Work?", "log_roi": "Log Return on Investment (ROI)"},
                    color_discrete_sequence=["#66c2a5", "#fc8d62"])
    fig2.update_xaxes(tickvals=[False, True], ticktext=["Original", "Derivative"])
    fig2.update_layout(showlegend=False, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)
    
    

# TAB 4: MID-BUDGET
with tab4:
    st.header("Who is making what?")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Derivative Share by Genre")
        st.markdown("Action, Sci-Fi, and Animation rely heavily on existing IP. Comedy and Romance are the last bastions of original storytelling.")
        top_genres = filtered_df["primary_genre"].value_counts().head(8).index
        genre_df = filtered_df[filtered_df["primary_genre"].isin(top_genres)]
        genre_derivative = pd.crosstab(genre_df["primary_genre"], genre_df["is_derivative"], normalize="index") * 100
        
        fig3 = px.bar(genre_derivative, x=genre_derivative.index, y=True, 
                        labels={"x": "Genre", "y": "% Derivative"}, color_discrete_sequence=["#fc8d62"])
        fig3.update_layout(template="plotly_dark", showlegend=False, yaxis_title="% of Movies that are Derivatives")
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.subheader("The IP Factories")
        st.markdown("Look at the top studios. Disney, Warner Bros, and Lionsgate have massive derivative shares, while indie labels like Fox Searchlight focus on originals.")
        top_studios = filtered_df["studio"].value_counts().head(10).index
        studio_df = filtered_df[filtered_df["studio"].isin(top_studios)]
        studio_stats = studio_df.groupby("studio")["is_derivative"].mean().mul(100).sort_values(ascending=True).reset_index()
        
        fig4 = px.bar(studio_stats, x="is_derivative", y="studio", orientation="h",
                        labels={"is_derivative": "% Derivative", "studio": ""}, color_discrete_sequence=["#00d4ff"])
        fig4.update_layout(template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)

    # TAB 5: THE DATA CATALOG
with tab5:
    st.header("What did we consider a 'Previous Work'?")
    st.markdown("""
    To identify derivative works, we used a combination of TMDB's **Collection data** (to find franchises and sequels) 
    and **Keyword tags** (to find adaptations of books, comics, games, and remakes). 
    
    Use the search bar or the filter below to see exactly how specific movies were classified.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Search bar
        search_query = st.text_input("🔍 Search for a movie title", "")
        
    with col2:
        # Filter by derivative type
        type_filter = st.selectbox(
            "Filter by Category", 
            options=["All", "Franchise/Sequel", "Adaptation", "Remake", "Original"]
        )
        
    # Apply filters
    table_df = filtered_df.copy()
    
    if search_query:
        table_df = table_df[table_df["title"].str.contains(search_query, case=False, na=False)]
        
    if type_filter != "All":
        if type_filter == "Original":
            table_df = table_df[table_df["is_derivative"] == False]
        else:
            # Match the exact string or a combination (e.g., "Franchise/Sequel & Adaptation")
            table_df = table_df[table_df["derivative_type"].str.contains(type_filter)]
            
    # Format columns for display
    display_df = table_df[[
        "title", "release_year", "derivative_type", "primary_genre", "studio", "budget", "revenue", "roi"
    ]].copy()
    
    # Rename columns for a cleaner look
    display_df.columns = ["Title", "Year", "Classification", "Genre", "Studio", "Budget ($)", "Revenue ($)", "ROI"]
    
    # Format currency and ROI
    display_df["Budget ($)"] = display_df["Budget ($)"].apply(lambda x: f"${x/1e6:,.1f}M" if pd.notnull(x) else "")
    display_df["Revenue ($)"] = display_df["Revenue ($)"].apply(lambda x: f"${x/1e6:,.1f}M" if pd.notnull(x) else "")
    display_df["ROI"] = display_df["ROI"].apply(lambda x: f"{x:.2f}x" if pd.notnull(x) else "")
    
    # Sort by Year descending
    display_df = display_df.sort_values("Year", ascending=False)
    
    # Display the interactive table
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True,
        height=600
    )
    
    # Show count
    st.caption(f"Showing {len(display_df)} movies based on current filters.")

st.markdown("---")
st.caption("Data sourced from TMDB API. Analysis includes top-grossing films with reported budget and revenue (1990-2025).")
