from . import pd,plt,KMeans,Patch

def Analysis3D(items:dict):
    N_CLUSTERS = 4

    records = []
    for item in items.values():
        try:
            price = float(item['Price'])
            feedback_pct = float(item['Feedback Percentage'])
            feedback_score = float(item['Feedback Score'])
            records.append({
                "Title": item["Title"],
                "Price": price,
                "Feedback Percentage": feedback_pct,
                "Feedback Score": feedback_score
            })
        except (ValueError, KeyError, TypeError):
            continue

    df = pd.DataFrame(records)

    for col in ["Price", "Feedback Percentage", "Feedback Score"]:
        df[f"{col} (Normalized)"] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())


    X = df[["Price (Normalized)", "Feedback Percentage (Normalized)", "Feedback Score (Normalized)"]].values
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=0)
    df["Cluster"] = kmeans.fit_predict(X)

    df["Cluster"] += 1
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(
        df["Price (Normalized)"],
        df["Feedback Percentage (Normalized)"],
        df["Feedback Score (Normalized)"],
        c=df["Cluster"],
        cmap='Set1',
        s=80,
        edgecolor='k',
        alpha=0.9
    )

    ax.view_init(elev=25, azim=135)
    ax.set_title("3D Clustering of Products", fontsize=14, fontweight='bold')
    ax.set_xlabel("Price (Normalized)")
    ax.set_ylabel("Feedback % (Normalized)")
    ax.set_zlabel("Feedback Score (Normalized)")

    colors = plt.cm.get_cmap('Set1', N_CLUSTERS)
    cluster_counts = df["Cluster"].value_counts().sort_index()
    legend_elements = [
        Patch(facecolor=colors(i - 1), edgecolor='k', label=f"Cluster {i}: {cluster_counts[i]} items")
        for i in range(1, N_CLUSTERS + 1)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1), title="Cluster Info")

    plt.tight_layout()


    return fig







