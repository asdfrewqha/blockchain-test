import tempfile
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import PercentFormatter


class PollVisualizer:
    def __init__(self, poll_data: dict):
        self.poll_data = poll_data
        sns.set_theme(style="whitegrid")

    def generate_visual_report(self) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            chart_path = tmpfile.name
        self._generate_chart(chart_path)
        return chart_path

    def _generate_chart(self, output_path: str):
        options = self.poll_data["options"]
        total_votes = self.poll_data["votes_count"]
        option_names = list(options.keys())
        votes_values = np.array(list(options.values()))
        percentages = (
            votes_values / total_votes * 100 if total_votes else np.zeros_like(votes_values)
        )

        fig, axes = plt.subplots(
            nrows=2,
            ncols=2,
            figsize=(14, 10),
            gridspec_kw={"width_ratios": [2, 1], "height_ratios": [2, 1]},
        )
        fig.subplots_adjust(top=0.88, hspace=0.35, wspace=0.25)

        # Заголовок и описание
        fig.suptitle(
            "\n".join(wrap(f"Анализ голосования: {self.poll_data['name']}", 80)),
            fontsize=20,
            fontweight="bold",
            y=0.97,
        )
        if self.poll_data.get("description"):
            fig.text(
                0.5,
                0.92,
                "\n".join(wrap(self.poll_data["description"], 90)),
                ha="center",
                fontsize=13,
                color="#555555",
            )

        # 1. Горизонтальный barplot (axes[0,0])
        sorted_idx = np.argsort(votes_values)[::-1]
        sorted_names = [option_names[i] for i in sorted_idx]
        sorted_votes = votes_values[sorted_idx]
        sorted_pct = percentages[sorted_idx]
        colors = sns.color_palette("viridis", len(option_names))
        winner_color = sns.color_palette("flare")[2]
        sorted_colors = [
            colors[i] if i != np.argmax(votes_values) else winner_color for i in sorted_idx
        ]

        ax_bar = axes[0, 0]
        y_pos = np.arange(len(sorted_names))
        bars = ax_bar.barh(y_pos, sorted_pct, color=sorted_colors, edgecolor="white", height=0.7)
        for i, (pct, vote_count) in enumerate(zip(sorted_pct, sorted_votes)):
            ax_bar.text(
                pct + 1,
                i,
                f"{vote_count} ({pct:.1f}%)",
                va="center",
                ha="left",
                color="#222",
                fontweight="bold",
                fontsize=11,
            )
        ax_bar.set_yticks(y_pos)
        ax_bar.set_yticklabels(sorted_names, fontsize=12)
        ax_bar.set_xlim(0, max(100, max(sorted_pct) * 1.1))
        ax_bar.xaxis.set_major_formatter(PercentFormatter())
        ax_bar.set_title("Распределение голосов", fontsize=15, pad=10)
        ax_bar.set_xlabel("Доля голосов (%)", fontsize=13)
        ax_bar.grid(axis="x", linestyle="--", alpha=0.6)
        sns.despine(ax=ax_bar, left=True, bottom=True)

        # 2. Круговая диаграмма (axes[0,1])
        ax_pie = axes[0, 1]
        ax_pie.set_title("Детальное соотношение", fontsize=14)
        wedges, texts, autotexts = ax_pie.pie(
            votes_values,
            labels=option_names,
            colors=colors,
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1},
            autopct=lambda p: f"{p:.0f}%" if p > 3 else "",
            pctdistance=0.8,
            textprops={"fontsize": 10},
        )

        # 3. Boxplot (axes[1,0])
        ax_box = axes[1, 0]
        sns.boxplot(y=votes_values, ax=ax_box, color="#3498db", width=0.4)
        ax_box.set_title("Распределение голосов", fontsize=14)
        ax_box.set_ylabel("Количество голосов", fontsize=12)
        ax_box.set_xlabel("")
        ax_box.tick_params(axis="y", labelsize=10)
        ax_box.grid(axis="y", linestyle="--", alpha=0.5)
        sns.despine(ax=ax_box, left=True)

        # 4. Таблица статистики (axes[1,1])
        ax_stats = axes[1, 1]
        ax_stats.axis("off")
        entropy = self._calculate_entropy(votes_values)
        gini = self._calculate_gini(votes_values)
        stats_data = [
            ["Всего голосов", f"{total_votes}"],
            ["Вариантов", f"{len(option_names)}"],
            [
                "Лидер",
                f"{option_names[np.argmax(votes_values)]} ({percentages[np.argmax(votes_values)]:.1f}%)",
            ],
            ["Энтропия", f"{entropy:.3f}"],
            ["Джини", f"{gini:.3f}"],
            ["Среднее", f"{np.mean(votes_values):.1f}"],
            ["Медиана", f"{np.median(votes_values):.1f}"],
            ["Ст. отклонение", f"{np.std(votes_values):.1f}"],
            ["Коэф. вариации", f"{(np.std(votes_values) / np.mean(votes_values) * 100):.1f}%"],
        ]
        table = ax_stats.table(
            cellText=stats_data,
            colLabels=["Метрика", "Значение"],
            loc="center",
            cellLoc="left",
            colWidths=[0.5, 0.5],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.5)

        plt.tight_layout(rect=[0, 0, 1, 0.93])
        plt.savefig(output_path, bbox_inches="tight", dpi=130)
        plt.close()

    def _calculate_entropy(self, votes):
        if np.sum(votes) == 0:
            return 0
        probabilities = np.array(votes) / np.sum(votes)
        return -np.sum(probabilities * np.log2(probabilities + 1e-10))

    def _calculate_gini(self, votes):
        votes_sorted = np.sort(votes)
        n = len(votes_sorted)
        cum_votes = np.cumsum(votes_sorted)
        return 1 - 2 * np.sum(cum_votes) / (n * cum_votes[-1]) + 1 / n


# # Пример данных опроса
# poll_example = {
#     "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
#     "name": "Лучший язык программирования 2023",
#     "votes_count": 150,
#     "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
#     "user_username": "tech_guru",
#     "description": "Голосование за самый перспективный язык программирования в 2023 году",
#     "options": {"Python": 65, "JavaScript": 45, "Rust": 25, "Go": 15},
# }

# visualizer = PollVisualizer(poll_example)
# chart_path = visualizer.generate_visual_report()
# print(f"График сохранен по пути: {chart_path}")
