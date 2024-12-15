import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from data_storage import DataProcessor

class DataAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Educational Data Analysis Tool")
        self.root.geometry("1400x900")
        self.loaded_files = None
        self.data_processor = DataProcessor("files")
        self.current_dataset = None
        self.df = None
        self.merged_df: Optional[pd.DataFrame] = None
        self.reshaped_df: Optional[pd.DataFrame] = None
        self.interaction_df: Optional[pd.DataFrame] = None
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.setup_gui()
        self.update_status("Ready")
        
    def setup_gui(self):
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        self.control_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.control_frame, weight=1)
        
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel, weight=3)
        
        self.setup_notebook()
        self.setup_control_panel()
        
    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_raw_data_tab()
        self.setup_processed_data_tab()
        self.setup_visualization_tab()
        self.setup_interaction_tab()
        
    def setup_control_panel(self):
        self.setup_data_loading()
        self.setup_data_processing()
        self.setup_analysis_options()
        self.setup_state_management()
        self.setup_status_bar()
        
    def setup_data_loading(self):
        load_frame = ttk.LabelFrame(self.control_frame, text="1. Data Loading")
        load_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        load_frame.columnconfigure(0, weight=1)
        
        ttk.Button(load_frame, text="Load CSV Files", 
                  command=self.load_csv_files).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(load_frame, text="Load Processed JSON", 
                  command=self.load_json_data).grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
    def setup_data_processing(self):
        """Set up the data processing section with all processing steps"""
        process_frame = ttk.LabelFrame(self.control_frame, text="2. Data Processing")
        process_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        process_frame.columnconfigure(0, weight=1)
        
        # Excluded components section
        ttk.Label(process_frame, text="Excluded Components:").grid(row=0, column=0, padx=5, pady=2)
        self.excluded_var = tk.StringVar(value="System,Folder")
        ttk.Entry(process_frame, textvariable=self.excluded_var).grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        
        # Processing buttons
        buttons_frame = ttk.Frame(process_frame)
        buttons_frame.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        buttons_frame.columnconfigure(0, weight=1)
        
        ttk.Button(buttons_frame, text="1. Process CSV", 
                command=self.process_csv).grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        ttk.Button(buttons_frame, text="2. Remove Excluded Components", 
                command=self.remove_components).grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        ttk.Button(buttons_frame, text="3. Rename Columns", 
                command=self.rename_columns).grid(row=2, column=0, padx=5, pady=2, sticky='ew')
        ttk.Button(buttons_frame, text="4. Merge Datasets", 
                command=self.merge_data).grid(row=3, column=0, padx=5, pady=2, sticky='ew')
        ttk.Button(buttons_frame, text="5. Reshape Data", 
                command=self.reshape_data).grid(row=4, column=0, padx=5, pady=2, sticky='ew')
        ttk.Button(buttons_frame, text="6. Count Interactions", 
                command=self.count_interactions).grid(row=5, column=0, padx=5, pady=2, sticky='ew')
        
    def setup_analysis_options(self):
        analysis_frame = ttk.LabelFrame(self.control_frame, text="3. Analysis Options")
        analysis_frame.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        
        analysis_frame.columnconfigure(0, weight=1)
        
        self.viz_type = tk.StringVar(value="interaction_heatmap")
        options = [
            ("Interaction Heatmap", "interaction_heatmap"),
            ("User Timeline", "user_timeline"),
            ("Component Distribution", "component_dist"),
            ("Monthly Trends", "monthly_trends"),
            ("User Activity Patterns", "user_patterns")
        ]
        
        for i, (text, value) in enumerate(options):
            ttk.Radiobutton(analysis_frame, text=text, 
                          variable=self.viz_type, 
                          value=value).grid(row=i, column=0, padx=5, pady=2, sticky='w')
        
        ttk.Button(analysis_frame, text="Generate Visualization", 
                  command=self.generate_visualization).grid(row=len(options), column=0, padx=5, pady=5, sticky='ew')
        
    def setup_state_management(self):
        state_frame = ttk.LabelFrame(self.control_frame, text="4. State Management")
        state_frame.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        
        self.state_info_var = tk.StringVar(value="No state loaded")
        ttk.Label(state_frame, textvariable=self.state_info_var).pack(pady=2)
        
        buttons_frame = ttk.Frame(state_frame)
        buttons_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(buttons_frame, text="Save State", 
                  command=self.save_state).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Clear State", 
                  command=self.clear_state).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Refresh State", 
                  command=self.refresh_state).pack(side=tk.LEFT, padx=2)
                  
    def setup_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.control_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, padding=(5, 2))
        status_bar.grid(row=4, column=0, sticky='ew', padx=5, pady=5)
        
    def setup_raw_data_tab(self):
        self.raw_data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.raw_data_frame, text="Raw Data")
        
        self.raw_data_tree = ttk.Treeview(self.raw_data_frame)
        self.setup_scrollbars(self.raw_data_frame, self.raw_data_tree)
        
    def setup_processed_data_tab(self):
        self.processed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processed_frame, text="Processed Data")
        
        self.processed_notebook = ttk.Notebook(self.processed_frame)
        self.processed_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.merged_frame = ttk.Frame(self.processed_notebook)
        self.reshaped_frame = ttk.Frame(self.processed_notebook)
        
        self.processed_notebook.add(self.merged_frame, text="Merged Data")
        self.processed_notebook.add(self.reshaped_frame, text="Reshaped Data")
        
        self.merged_tree = ttk.Treeview(self.merged_frame)
        self.reshaped_tree = ttk.Treeview(self.reshaped_frame)
        
        self.setup_scrollbars(self.merged_frame, self.merged_tree)
        self.setup_scrollbars(self.reshaped_frame, self.reshaped_tree)

    def setup_visualization_tab(self):
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualizations")
        
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_interaction_tab(self):
        self.interaction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.interaction_frame, text="Interaction Counts")
        
        self.interaction_tree = ttk.Treeview(self.interaction_frame)
        self.setup_scrollbars(self.interaction_frame, self.interaction_tree)
        
    def setup_scrollbars(self, parent, tree):
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
    def update_raw_data_view(self):
        try:
            if not self.df is None:
                self.raw_data_tree.delete(*self.raw_data_tree.get_children())
                
                columns = list(self.df.columns)
                self.raw_data_tree["columns"] = columns
                
                self.raw_data_tree.column("#0", width=0, stretch=tk.NO)
                for col in columns:
                    self.raw_data_tree.column(col, anchor=tk.W, width=100)
                    self.raw_data_tree.heading(col, text=col, anchor=tk.W)
                
                for idx, row in self.df.iterrows():
                    self.raw_data_tree.insert("", tk.END, values=list(row))
                    
        except Exception as e:
            self.update_status("Failed to update raw data view", error=True)
            messagebox.showerror("Error", str(e))
            
    def update_processed_data_view(self):
        try:
            if self.merged_df is not None:
                self.update_treeview(self.merged_tree, self.merged_df)
                
            if self.reshaped_df is not None:
                self.update_treeview(self.reshaped_tree, self.reshaped_df)
                
            if self.interaction_df is not None:
                self.update_treeview(self.interaction_tree, self.interaction_df)
                
        except Exception as e:
            self.update_status("Failed to update processed data view", error=True)
            messagebox.showerror("Error", str(e))
            
    def update_treeview(self, tree: ttk.Treeview, df: pd.DataFrame):
        tree.delete(*tree.get_children())
        
        columns = list(df.columns)
        tree["columns"] = columns
        
        tree.column("#0", width=0, stretch=tk.NO)
        for col in columns:
            tree.column(col, anchor=tk.W, width=100)
            tree.heading(col, text=col, anchor=tk.W)
        
        for idx, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))
            
    def load_csv_files(self):
        """Load CSV files and display in raw data tab without processing"""
        try:
            files = filedialog.askopenfilenames(
                title="Select CSV Files",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not files:
                return
                
            # Store file paths for later processing
            self.loaded_files = files
            
            # Read and display CSV files
            dfs = []
            for file in files:
                df = pd.read_csv(file)
                df['Source'] = Path(file).stem
                dfs.append(df)
            
            self.df = pd.concat(dfs, ignore_index=True)
            self.update_raw_data_view()
            self.update_status(f"Loaded {len(files)} CSV files successfully")
            messagebox.showinfo("Success", f"Successfully loaded {len(files)} CSV files!")
            
        except Exception as e:
            self.update_status("Failed to load CSV files", error=True)
            messagebox.showerror("Error", f"Error loading CSV files: {str(e)}")   

    def load_json_data(self):
        try:
            file = filedialog.askopenfilename(
                title="Select JSON File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file:
                return
                
            with open(file, 'r') as f:
                data = json.load(f)
                self.current_dataset = data['data']
                self.prepare_dataframe()
                self.update_raw_data_view()
                
            self.update_status("JSON data loaded successfully")
            messagebox.showinfo("Success", "JSON data loaded successfully!")
            
        except Exception as e:
            self.update_status("Failed to load JSON data", error=True)
            messagebox.showerror("Error", f"Error loading JSON data: {str(e)}")
            
    def prepare_dataframe(self):
        if not self.current_dataset:
            return
            
        dfs = []
        for dataset_name, records in self.current_dataset.items():
            df = pd.DataFrame(records)
            df['Source'] = dataset_name
            dfs.append(df)
        
        self.df = pd.concat(dfs, ignore_index=True)
        
    def merge_data(self):
        try:
            if not self.data_processor.data:
                raise ValueError("Please load data files first!")
            
            self.merged_df = self.data_processor.merge_datasets()
            self.update_processed_data_view()
            self.notebook.select(1)  # Switch to Processed Data tab
            self.update_status(f"Merged {len(self.merged_df)} records successfully")
            messagebox.showinfo("Success", f"Merged {len(self.merged_df)} records successfully!")
            
        except Exception as e:
            self.update_status("Merge operation failed", error=True)
            messagebox.showerror("Error", str(e))
            
    def reshape_data(self):
        try:
            if self.merged_df is None:
                raise ValueError("Please merge datasets first!")
            
            self.reshaped_df = self.data_processor.reshape_data(self.merged_df)
            self.update_processed_data_view()
            self.notebook.select(1)  # Switch to Processed Data tab
            self.processed_notebook.select(1)  # Switch to Reshaped Data tab
            self.update_status("Data reshaped successfully")
            messagebox.showinfo("Success", "Data reshaped successfully!")
            
        except Exception as e:
            self.update_status("Reshape operation failed", error=True)
            messagebox.showerror("Error", str(e))
            
    def count_interactions(self):
        try:
            if self.merged_df is None:
                raise ValueError("Please merge datasets first!")
            
            self.interaction_df = self.data_processor.count_interactions(self.merged_df)
            self.update_processed_data_view()
            self.notebook.select(3)  # Switch to Interaction Counts tab
            self.update_status("Interaction counts generated successfully")
            messagebox.showinfo("Success", "Interaction counts generated successfully!")
            
        except Exception as e:
            self.update_status("Counting interactions failed", error=True)
            messagebox.showerror("Error", str(e))

    def process_csv(self):
        """Process loaded CSV files"""
        try:
            if not hasattr(self, 'loaded_files') or not self.loaded_files:
                raise ValueError("Please load CSV files first!")
                
            self.data_processor.process_csv_files(*self.loaded_files)
            self.refresh_state()
            self.update_status("CSV files processed successfully")
            messagebox.showinfo("Success", "CSV files processed successfully!")
            
        except Exception as e:
            self.update_status("Processing failed", error=True)
            messagebox.showerror("Error", str(e))

    def remove_components(self):
        """Remove excluded components from processed data"""
        try:
            if not self.data_processor.data:
                raise ValueError("Please process CSV files first!")
                
            self.data_processor.remove_excluded_components()
            self.refresh_state()
            self.update_status("Excluded components removed successfully")
            messagebox.showinfo("Success", "Excluded components removed successfully!")
            
        except Exception as e:
            self.update_status("Component removal failed", error=True)
            messagebox.showerror("Error", str(e))

    def rename_columns(self):
        """Rename columns in processed data"""
        try:
            if not self.data_processor.data:
                raise ValueError("Please process CSV files first!")
                
            self.data_processor.rename_user_column()
            self.refresh_state()
            self.update_status("Columns renamed successfully")
            messagebox.showinfo("Success", "Columns renamed successfully!")
            
        except Exception as e:
            self.update_status("Column renaming failed", error=True)
            messagebox.showerror("Error", str(e))
            
    def generate_visualization(self):
        try:
            if self.merged_df is None:
                raise ValueError("Please process data first!")
                
            self.ax.clear()
            
            viz_type = self.viz_type.get()
            if viz_type == "interaction_heatmap":
                self._plot_interaction_heatmap()
            elif viz_type == "user_timeline":
                self._plot_user_timeline()
            elif viz_type == "component_dist":
                self._plot_component_distribution()
            elif viz_type == "monthly_trends":
                self._plot_monthly_trends()
            elif viz_type == "user_patterns":
                self._plot_user_patterns()
                
            plt.tight_layout()
            self.canvas.draw()
            self.notebook.select(2)  # Switch to Visualizations tab
            self.update_status("Visualization generated successfully")
            
        except Exception as e:
            self.update_status("Visualization failed", error=True)
            messagebox.showerror("Error", str(e))
            
    def _plot_interaction_heatmap(self):
        if self.interaction_df is None:
            raise ValueError("Please generate interaction counts first!")
            
        pivot = pd.pivot_table(
            self.interaction_df,
            values='Interaction_Count',
            index='User_ID',
            columns='Component',
            fill_value=0
        )
        
        sns.heatmap(pivot, cmap='YlOrRd', ax=self.ax)
        self.ax.set_title('User-Component Interaction Heatmap')
        
    def _plot_user_timeline(self):
        user_activity = self.merged_df.groupby('User_ID').size()
        user_activity.plot(kind='bar', ax=self.ax)
        self.ax.set_title('User Activity Distribution')
        plt.xticks(rotation=45)
        
    def _plot_component_distribution(self):
        component_dist = self.merged_df['Component'].value_counts()
        component_dist.plot(kind='pie', ax=self.ax, autopct='%1.1f%%')
        self.ax.set_title('Component Usage Distribution')
        
    def _plot_monthly_trends(self):
        monthly = self.merged_df.groupby('Month').size()
        monthly.plot(kind='line', marker='o', ax=self.ax)
        self.ax.set_title('Monthly Activity Trends')
        plt.xticks(rotation=45)
        
    def _plot_user_patterns(self):
        patterns = self.merged_df.groupby(['User_ID', 'Component']).size().unstack(fill_value=0)
        sns.clustermap(patterns, cmap='viridis')
        self.ax.set_title('User Activity Patterns')
        
    def save_state(self):
        try:
            self.data_processor._save_state()
            self.update_status("State saved successfully")
            self.refresh_state()
        except Exception as e:
            self.update_status("Failed to save state", error=True)
            messagebox.showerror("Error", f"Error saving state: {str(e)}")
            
    def clear_state(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the current state?"):
            try:
                self.data_processor.clear_state()
                self.merged_df = None
                self.reshaped_df = None
                self.interaction_df = None
                self.update_status("State cleared successfully")
                self.refresh_state()
            except Exception as e:
                self.update_status("Failed to clear state", error=True)
                messagebox.showerror("Error", f"Error clearing state: {str(e)}")
                
    def refresh_state(self):
        try:
            summary = self.data_processor.get_state_summary()
            info_text = (
                f"Processed Files: {summary['processed_files']}\n"
                f"Total Records: {summary['total_records']}\n"
                f"Datasets: {', '.join(summary['datasets'])}\n"
                f"Last Updated: {summary['last_updated']}"
            )
            self.state_info_var.set(info_text)
            self.update_status("State refreshed")
        except Exception as e:
            self.update_status("Failed to refresh state", error=True)
            messagebox.showerror("Error", f"Error refreshing state: {str(e)}")
            
    def update_status(self, message: str, error: bool = False):
        prefix = "⚠ " if error else "✓ "
        self.status_var.set(f"{prefix}{message}")