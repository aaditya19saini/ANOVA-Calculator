import numpy as np
from scipy import stats

class ANOVA:
    def __init__(self, data):
        """
        Initialize the ANOVA calculator with data.
        
        Args:
            data: Can be a list of lists, a dictionary of lists, or a numpy array.
                  Represents groups of samples.
        """
        self.groups = []
        self.group_names = []
        
        # Standardize input to list of numpy arrays
        if isinstance(data, dict):
            for name, group in data.items():
                self.groups.append(np.array(group, dtype=float))
                self.group_names.append(name)
        elif isinstance(data, (list, tuple, np.ndarray)):
             # potential list of lists or 2D array
            try:
                # Check if it's a 2D array or list of lists
                for i, group in enumerate(data):
                    self.groups.append(np.array(group, dtype=float))
                    self.group_names.append(f"Group {i+1}")
            except Exception:
                 # Fallback if it's a single 1D array (one group? strictly not ANOVA but handle gracefully?)
                 self.groups.append(np.array(data, dtype=float))
                 self.group_names.append("Group 1")
        else:
            raise ValueError("Unsupported data format. Please provide a list of lists, numpy array, or dictionary.")

        self.k = len(self.groups) # number of groups
        self.n_total = sum(len(g) for g in self.groups) # total number of samples

    def calculate(self):
        """
        Perform one-way ANOVA calculations.
        
        Returns:
            dict: A dictionary containing all ANOVA statistics.
        """
        # 1. Calculate sums and means
        group_sums = [np.sum(g) for g in self.groups]
        group_means = [np.mean(g) for g in self.groups]
        grand_mean = np.sum([np.sum(g) for g in self.groups]) / self.n_total
        
        # 2. Sum of Squares
        # SS_total: sum((x - grand_mean)^2) for all x
        ss_total = sum(np.sum((g - grand_mean)**2) for g in self.groups)
        
        # SS_between (Treatment): sum(n_i * (mean_i - grand_mean)^2)
        ss_between = sum(len(g) * (mean - grand_mean)**2 for g, mean in zip(self.groups, group_means))
        
        # SS_within (Error): sum((x - mean_i)^2) for all groups
        ss_within = sum(np.sum((g - mean)**2) for g, mean in zip(self.groups, group_means))
        
        # 3. Degrees of Freedom
        df_between = self.k - 1
        df_within = self.n_total - self.k
        df_total = self.n_total - 1
        
        # 4. Mean Squares
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within
        
        # 5. F-statistic
        f_stat = ms_between / ms_within
        
        # 6. P-value
        p_value = stats.f.sf(f_stat, df_between, df_within)
        
        # Return results
        return {
            "SS": {"between": ss_between, "within": ss_within, "total": ss_total},
            "df": {"between": df_between, "within": df_within, "total": df_total},
            "MS": {"between": ms_between, "within": ms_within},
            "F": f_stat,
            "p_value": p_value,
            "summary": self._format_summary(ss_between, ss_within, ss_total, 
                                          df_between, df_within, df_total,
                                          ms_between, ms_within, f_stat, p_value)
        }

    def _format_summary(self, ssb, ssw, sst, dfb, dfw, dft, msb, msw, f, p):
        """Helper to format the output as a string table."""
        header = f"{'Source':<15} | {'SS':<10} | {'df':<5} | {'MS':<10} | {'F':<8} | {'p-value':<8}"
        row1 = f"{'Between Groups':<15} | {ssb:<10.2f} | {dfb:<5} | {msb:<10.2f} | {f:<8.2f} | {p:<8.4f}"
        row2 = f"{'Within Groups':<15} | {ssw:<10.2f} | {dfw:<5} | {msw:<10.2f} | {'-':<8} | {'-':<8}"
        row3 = f"{'Total':<15} | {sst:<10.2f} | {dft:<5} | {'-':<10} | {'-':<8} | {'-':<8}"
        return f"{header}\n{'-'*70}\n{row1}\n{row2}\n{row3}"

if __name__ == "__main__":
    # Test with the user's original data
    m = np.array([[12.5, 13.1, 11.8, 12.9, 12.2, 13.5, 12. ],
                  [15.2, 16., 14.8, 15.5, 16.2, 15.9, 14.5],
                  [18.1, 17.9, 19.2, 18.5, 17.6, 18.8, 19. ]])
    
    anova = ANOVA(m)
    results = anova.calculate()
    print(results['summary'])
