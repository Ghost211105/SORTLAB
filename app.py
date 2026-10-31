import time
import random
import io
import statistics
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SortLab | DAA Performance Studio", page_icon="⚡", layout="wide")

# -------------------- Visual identity --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:linear-gradient(135deg,#fff8ef 0%,#f3f7ff 48%,#f8f1ff 100%);}
.block-container {padding-top:1.6rem;max-width:1450px;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;color:#19234a;}
.hero {padding:30px 34px;border-radius:26px;color:white;background:linear-gradient(110deg,#5b43e8,#168be8 58%,#16b8a6);box-shadow:0 14px 35px #5367b52b;margin-bottom:20px;}
.hero h1 {color:white;font-size:2.5rem;margin:0}.hero p {color:#eef5ff;font-size:1.05rem;margin:8px 0 0}
.metric-card {background:white;border:1px solid #e7eaff;border-radius:18px;padding:17px 20px;box-shadow:0 8px 24px #35447712;min-height:100px}
.metric-label {font-size:.82rem;color:#65708e;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.metric-value {font-family:'Space Grotesk';font-size:1.75rem;color:#27356d;font-weight:700}
.metric-note {font-size:.82rem;color:#78829c}
.section-tag {display:inline-block;background:#e9e6ff;color:#5943d7;padding:5px 11px;border-radius:20px;font-size:.78rem;font-weight:800;letter-spacing:.05em}
div[data-testid="stSidebar"] {background:linear-gradient(180deg,#f0edff,#eaf6ff);}
.stButton>button[kind="primary"] {background:linear-gradient(90deg,#6045e8,#168be8);border:0;border-radius:12px;font-weight:800;}
.stButton>button {border-radius:11px}
div[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden}
div[data-testid="stTabs"] button {font-weight:700}
.tip {background:#fff4d9;border-left:5px solid #ffb52e;padding:13px 16px;border-radius:10px;color:#624b17}
.good {background:#e3fbf3;border-left:5px solid #18b78b;padding:13px 16px;border-radius:10px;color:#155b4b}
</style>
""", unsafe_allow_html=True)

# -------------------- Instrumented algorithms --------------------
def bubble_sort(arr):
    a=list(arr); c=s=m=0
    for i in range(len(a)):
        changed=False
        for j in range(len(a)-i-1):
            c+=1
            if a[j]>a[j+1]:
                a[j],a[j+1]=a[j+1],a[j]; s+=1; m+=3; changed=True
        if not changed: break
    return a,c,s,m

def selection_sort(arr):
    a=list(arr); c=s=m=0
    for i in range(len(a)):
        k=i
        for j in range(i+1,len(a)):
            c+=1
            if a[j]<a[k]: k=j
        if k!=i: a[i],a[k]=a[k],a[i]; s+=1; m+=3
    return a,c,s,m

def insertion_sort(arr):
    a=list(arr); c=s=m=0
    for i in range(1,len(a)):
        key=a[i]; j=i-1
        while j>=0:
            c+=1
            if a[j]>key: a[j+1]=a[j]; m+=1; j-=1
            else: break
        a[j+1]=key; m+=1
    return a,c,s,m

def merge_sort(arr):
    c=[0]; m=[0]
    def rec(a):
        if len(a)<=1:return a
        mid=len(a)//2; left=rec(a[:mid]); right=rec(a[mid:]); out=[]; i=j=0
        while i<len(left) and j<len(right):
            c[0]+=1
            if left[i]<=right[j]:out.append(left[i]);i+=1
            else:out.append(right[j]);j+=1
            m[0]+=1
        out.extend(left[i:]);out.extend(right[j:]);m[0]+=len(left)-i+len(right)-j
        return out
    return (lambda r:(r,c[0],0,m[0]))(rec(list(arr)))

def quick_sort(arr):
    a=list(arr); c=[0]; s=[0]; m=[0]
    def part(lo,hi):
        pivot=a[hi]; i=lo-1
        for j in range(lo,hi):
            c[0]+=1
            if a[j]<=pivot:
                i+=1
                if i!=j:a[i],a[j]=a[j],a[i];s[0]+=1;m[0]+=3
        if i+1!=hi:a[i+1],a[hi]=a[hi],a[i+1];s[0]+=1;m[0]+=3
        return i+1
    # Explicit stack avoids Python recursion-depth failures on unfavourable inputs.
    stack=[(0,len(a)-1)]
    while stack:
        lo,hi=stack.pop()
        if lo<hi:
            p=part(lo,hi)
            if p-lo < hi-p: stack.extend([(p+1,hi),(lo,p-1)])
            else: stack.extend([(lo,p-1),(p+1,hi)])
    return a,c[0],s[0],m[0]

def heap_sort(arr):
    a=list(arr); c=s=m=0
    def sift(n,i):
        nonlocal c,s,m
        largest=i; l=2*i+1; r=2*i+2
        if l<n:
            c+=1
            if a[l]>a[largest]:largest=l
        if r<n:
            c+=1
            if a[r]>a[largest]:largest=r
        if largest!=i:a[i],a[largest]=a[largest],a[i];s+=1;m+=3;sift(n,largest)
    for i in range(len(a)//2-1,-1,-1):sift(len(a),i)
    for end in range(len(a)-1,0,-1):
        a[0],a[end]=a[end],a[0];s+=1;m+=3;sift(end,0)
    return a,c,s,m

def shell_sort(arr):
    a=list(arr); c=s=m=0; gap=len(a)//2
    while gap>0:
        for i in range(gap,len(a)):
            temp=a[i];j=i
            while j>=gap:
                c+=1
                if a[j-gap]>temp:a[j]=a[j-gap];m+=1;j-=gap
                else:break
            a[j]=temp;m+=1
        gap//=2
    return a,c,s,m

ALGORITHMS={"Bubble Sort":bubble_sort,"Selection Sort":selection_sort,"Insertion Sort":insertion_sort,
            "Merge Sort":merge_sort,"Quick Sort":quick_sort,"Heap Sort":heap_sort,"Shell Sort":shell_sort,
            "Python Timsort":None}
META={
"Bubble Sort":("O(n)","O(n²)","O(n²)","Stable","In-place"),
"Selection Sort":("O(n²)","O(n²)","O(n²)","Not stable","In-place"),
"Insertion Sort":("O(n)","O(n²)","O(n²)","Stable","In-place"),
"Merge Sort":("O(n log n)","O(n log n)","O(n log n)","Stable","O(n) extra"),
"Quick Sort":("O(n log n)","O(n log n)","O(n²)","Not stable","O(log n) stack avg."),
"Heap Sort":("O(n log n)","O(n log n)","O(n log n)","Not stable","In-place"),
"Shell Sort":("Depends on gaps","Depends on gaps","O(n²) typical","Not stable","In-place"),
"Python Timsort":("O(n)","O(n log n)","O(n log n)","Stable","O(n) worst-case")
}

def synthetic_students(n,seed):
    rng=random.Random(seed)
    return pd.DataFrame({"student_id":[f"ST{i+1:05d}" for i in range(n)],
      "name":[f"Student_{i+1}" for i in range(n)],"marks":[rng.randint(0,100) for _ in range(n)],
      "attendance":[rng.randint(40,100) for _ in range(n)]})

def synthetic_sensors(n,seed):
    rng=random.Random(seed); start=pd.Timestamp("2026-01-01")
    return pd.DataFrame({"timestamp":[start+pd.Timedelta(seconds=i*5) for i in range(n)],
      "temperature":[round(rng.uniform(10,42),2) for _ in range(n)],
      "humidity":[round(rng.uniform(20,95),2) for _ in range(n)]}).sample(frac=1,random_state=seed).reset_index(drop=True)

def apply_pattern(values,pattern,seed):
    a=list(values); rng=random.Random(seed)
    if pattern=="Already sorted": return sorted(a)
    if pattern=="Reverse sorted": return sorted(a,reverse=True)
    if pattern=="Nearly sorted":
        a=sorted(a)
        for _ in range(max(1,len(a)//20)):
            if len(a)>1:
                i=rng.randrange(len(a));j=rng.randrange(len(a));a[i],a[j]=a[j],a[i]
        return a
    return a

def recommendation(n,pattern):
    if n<=80:return "Insertion Sort", "Small inputs have low overhead; insertion sort is simple and adaptive."
    if pattern=="Already sorted" and n<3000:return "Insertion Sort", "Insertion sort can approach O(n) on already sorted input."
    if n>=10000:return "Merge Sort", "Predictable O(n log n) performance is safer for large datasets."
    return "Quick Sort", "A strong general-purpose classroom choice with average O(n log n) behaviour."

# -------------------- Header and controls --------------------
st.markdown('<div class="hero"><h1>⚡ SortLab</h1><p>DAA Performance Studio · Explore, visualize and benchmark sorting algorithms on real-world style data.</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🧪 Experiment setup")
    source=st.radio("Choose dataset",["Synthetic student records","Synthetic sensor logs","Upload your CSV"])
    n=st.select_slider("Number of records",options=[10,25,50,100,250,500,1000,2000,5000,10000],value=500)
    seed=st.number_input("Random seed",min_value=0,max_value=999999,value=42,step=1)
    pattern=st.selectbox("Input arrangement",["Random","Already sorted","Reverse sorted","Nearly sorted"])
    upload=st.file_uploader("Upload CSV file",type=["csv"]) if source=="Upload your CSV" else None
    st.caption("Tip: use 10–500 records for Bubble, Selection and Insertion Sort. Large quadratic runs can take a long time.")
if source=="Synthetic student records": df=synthetic_students(n,int(seed))
elif source=="Synthetic sensor logs": df=synthetic_sensors(n,int(seed))
elif upload is not None:
    try: df=pd.read_csv(upload)
    except Exception as e: st.error(f"CSV could not be read: {e}");st.stop()
else: st.info("Upload a CSV from the sidebar to begin.");st.stop()
if df.empty: st.warning("The selected dataset is empty.");st.stop()
numeric_cols=list(df.select_dtypes(include="number").columns)
if not numeric_cols: st.error("This lab currently benchmarks numeric columns. Add at least one numeric column to your CSV.");st.stop()
sort_col=st.selectbox("🎯 Select the numeric field to sort",numeric_cols)
raw=df[sort_col].dropna().tolist()
if len(raw)!=len(df): st.warning("Rows with missing values in this field are excluded from sorting.")
values=apply_pattern(raw,pattern,int(seed))
data_tab,bench_tab,visual_tab,learn_tab=st.tabs(["📊 Dataset overview","🏁 Benchmark arena","🎞️ Algorithm visualizer","🧠 DAA knowledge hub"])

with data_tab:
    st.markdown('<span class="section-tag">DATA INTELLIGENCE</span>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    for col,label,val,note in [(a,"TOTAL RECORDS",f"{len(df):,}","Rows loaded"),(b,"DATA FIELDS",len(df.columns),"Columns detected"),(c,"SORT KEY",sort_col,"Selected numeric field"),(d,"INPUT PATTERN",pattern,"Experiment condition")]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)
    st.write("")
    left,right=st.columns([1.4,1])
    with left:
        st.subheader("Dataset preview")
        st.dataframe(df.head(15),use_container_width=True,hide_index=True)
    with right:
        st.subheader("Distribution snapshot")
        fig=px.histogram(pd.DataFrame({sort_col:values}),x=sort_col,nbins=24,
                         color_discrete_sequence=["#7658e8"],title=f"Distribution of {sort_col}")
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=45,b=10))
        st.plotly_chart(fig,use_container_width=True)
    st.subheader("Smart algorithm suggestion")
    alg,why=recommendation(len(values),pattern)
    st.markdown(f'<div class="good"><b>✨ Suggested: {alg}</b><br>{why}</div>',unsafe_allow_html=True)
    st.caption("The recommendation is a teaching heuristic, not a universal claim. Hardware, duplicates and implementation details affect actual results.")

with bench_tab:
    st.markdown('<span class="section-tag">CONTROLLED EXPERIMENT</span>',unsafe_allow_html=True)
    st.subheader("Configure your benchmark")
    defaults=["Insertion Sort","Merge Sort","Quick Sort","Heap Sort","Shell Sort","Python Timsort"]
    chosen=st.multiselect("Algorithms to compare",list(ALGORITHMS),default=defaults)
    order=st.radio("Output order",["Ascending","Descending"],horizontal=True)
    repeats=st.slider("Repeated timing trials",1,7,3)
    if len(values)>3000:
        st.markdown('<div class="tip">Large dataset detected. Quadratic algorithms may take a very long time. Consider disabling Bubble, Selection and Insertion Sort.</div>',unsafe_allow_html=True)
    if st.button("🚀 Run performance experiment",type="primary",use_container_width=True):
        if not chosen: st.warning("Select at least one algorithm.")
        else:
            target=sorted(values,reverse=(order=="Descending")); rows=[]; outputs={}
            for name in chosen:
                if name in ("Bubble Sort","Selection Sort","Insertion Sort") and len(values)>5000:
                    st.warning(f"{name} skipped for safety on more than 5,000 values.");continue
                times=[]; result=None; comp=swaps=moves=None
                for _ in range(repeats):
                    t0=time.perf_counter()
                    if ALGORITHMS[name] is None:
                        result=sorted(values);comp=swaps=moves=None
                    else: result,comp,swaps,moves=ALGORITHMS[name](values)
                    times.append((time.perf_counter()-t0)*1000)
                if order=="Descending": result=list(reversed(result))
                outputs[name]=result
                rows.append({"Algorithm":name,"Best (ms)":round(min(times),4),"Median (ms)":round(statistics.median(times),4),
                             "Comparisons":comp,"Swaps":swaps,"Moves (est.)":moves,"Correct":result==target})
            if rows:
                result_df=pd.DataFrame(rows).sort_values("Median (ms)")
                st.session_state["lab_results"]=result_df
                st.session_state["lab_outputs"]=outputs
                st.session_state["lab_df"]=df.copy()
                st.session_state["lab_col"]=sort_col
                st.session_state["lab_order"]=order
                st.session_state["lab_target"]=target
    if "lab_results" in st.session_state:
        r=st.session_state["lab_results"]
        st.divider();st.subheader("Experiment results")
        winner=r.iloc[0]
        x1,x2,x3=st.columns(3)
        for col,label,val,note in [(x1,"FASTEST MEDIAN",winner["Algorithm"],f'{winner["Median (ms)"]} ms median'),(x2,"ALGORITHMS TESTED",len(r),"Completed runs"),(x3,"CORRECTNESS",f'{int(r["Correct"].sum())}/{len(r)}',"Matched reference output")]:
            with col:st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)
        st.dataframe(r,use_container_width=True,hide_index=True)
        chart=px.bar(r,x="Algorithm",y="Median (ms)",color="Algorithm",text="Median (ms)",title="Median runtime · lower is better",
                     color_discrete_sequence=["#6548e8","#168be8","#12b99a","#ff9f43","#ec5c9a","#7c8da8"])
        chart.update_layout(showlegend=False,plot_bgcolor="white",paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart,use_container_width=True)
        ops=r.dropna(subset=["Comparisons"])
        if not ops.empty:
            fig=px.bar(ops,x="Algorithm",y="Comparisons",color="Algorithm",title="Key comparisons counted by implementation",
                       color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(showlegend=False,plot_bgcolor="white",paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
        st.subheader("Sorted output explorer")
        selected=st.selectbox("Choose algorithm output",list(st.session_state["lab_outputs"]))
        sorted_df=st.session_state["lab_df"].copy()
        # Stable row-level sort preserves all original columns.
        sorted_df=sorted_df.sort_values(st.session_state["lab_col"],ascending=st.session_state["lab_order"]=="Ascending",kind="stable")
        st.dataframe(sorted_df.head(100),use_container_width=True)
        st.download_button("⬇️ Download sorted dataset",sorted_df.to_csv(index=False).encode(), "sorted_dataset.csv","text/csv")
        st.download_button("⬇️ Download benchmark results",r.to_csv(index=False).encode(),"sortlab_benchmark.csv","text/csv")
        report=("SORTLAB BENCHMARK REPORT\n"+f"Records: {len(values)}\nSort key: {sort_col}\nInput pattern: {pattern}\nOrder: {order}\n\n"+r.to_string(index=False))
        st.download_button("📄 Download experiment summary",report.encode(),"sortlab_experiment_report.txt","text/plain")

with visual_tab:
    st.markdown('<span class="section-tag">ALGORITHM ANIMATION</span>',unsafe_allow_html=True)
    st.subheader("Bubble Sort · step-by-step")
    st.write("A lightweight visual trace shows how adjacent elements move. The visualizer is intentionally limited to 30 values so each operation remains understandable.")
    demo=values[:min(30,len(values))]
    if len(demo)>1:
        if st.button("Generate Bubble Sort trace",key="trace"):
            a=list(demo);snaps=[(0,a.copy(),"Initial array")]
            for i in range(len(a)):
                swapped=False
                for j in range(len(a)-i-1):
                    if a[j]>a[j+1]:
                        a[j],a[j+1]=a[j+1],a[j];swapped=True
                        if len(snaps)<250:snaps.append((j,a.copy(),f"Swap positions {j} and {j+1}"))
                if not swapped:break
            snaps.append((len(a)-1,a.copy(),"Sorted array"))
            st.session_state["bubble_trace"]=snaps
        if "bubble_trace" in st.session_state:
            trace=st.session_state["bubble_trace"]
            step=st.slider("Move through sorting steps",0,len(trace)-1,0)
            idx,arr,caption=trace[step]
            fig=go.Figure(go.Bar(x=list(range(len(arr))),y=arr,marker_color=["#ff9f43" if i in (idx,idx+1) else "#5b55df" for i in range(len(arr))]))
            fig.update_layout(title=caption,xaxis_title="Array index",yaxis_title="Value",plot_bgcolor="white",paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
            st.caption(f"Step {step+1} of {len(trace)} · Orange bars highlight the current swap area.")
    else: st.info("Choose a dataset with at least two values to visualize sorting.")
    st.markdown("#### What is happening?")
    st.write("Bubble Sort repeatedly compares neighbouring values. If they are out of order, it swaps them. After each complete pass, the largest remaining value settles at the end.")
    st.markdown('<div class="tip">Complexity insight: best case O(n) with the early-exit optimization; average and worst case O(n²). The trace is a teaching aid and does not represent benchmark timing.</div>',unsafe_allow_html=True)

with learn_tab:
    st.markdown('<span class="section-tag">THEORY MEETS PRACTICE</span>',unsafe_allow_html=True)
    st.subheader("Algorithm complexity matrix")
    matrix=[]
    for name,meta in META.items():
        matrix.append({"Algorithm":name,"Best":meta[0],"Average":meta[1],"Worst":meta[2],"Stability":meta[3],"Space":meta[4]})
    st.dataframe(pd.DataFrame(matrix),use_container_width=True,hide_index=True)
    st.subheader("How to read your experiment")
    with st.expander("Runtime vs. operation count"):
        st.write("Runtime is wall-clock time measured with perf_counter. Comparisons and moves are source-level counters. A lower operation count does not always mean lower runtime because Python overhead, memory access and implementation details matter.")
    with st.expander("Why input arrangement matters"):
        st.write("Insertion and optimized Bubble Sort can benefit from already-sorted data. Reverse-sorted data can expose quadratic behaviour. Merge Sort has predictable O(n log n) time regardless of input arrangement.")
    with st.expander("Stable vs. unstable sorting"):
        st.write("A stable algorithm preserves the original relative order of records with equal keys. Stability matters when sorting records by multiple fields in successive passes.")
    with st.expander("Benchmark methodology"):
        st.write("All algorithms receive the same values. Timing excludes CSV loading and chart rendering. Median and best times are reported across repeated trials. Correctness is checked against Python's sorted() reference.")
    st.subheader("Implementation details")
    st.write("Built with Python, Streamlit, Pandas and Plotly. Custom implementations instrument comparisons, swaps and estimated data movements. Python Timsort is included as a production baseline.")
    st.caption("Academic note: results depend on machine load, Python version, dataset distribution and implementation choices. Repeat experiments and discuss trends rather than claiming universal winners.")

st.markdown("---")
st.markdown("<center><b>SortLab · Design and Analysis of Algorithms</b><br><span style='color:#7b849e'>Built for experimentation, not just demonstration · B.Tech PBL</span></center>",unsafe_allow_html=True)
