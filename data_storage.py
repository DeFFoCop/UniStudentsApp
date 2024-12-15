import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple, Optional
from pathlib import Path
import pandas as pd

class DataProcessor:
    def __init__(self, backup_file_path: str):
        self.backup_file_path = Path(backup_file_path)
        self.state_file = self.backup_file_path / "application_state.json"
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.excluded_components: Set[str] = {'System', 'Folder'}
        self.column_mappings = {
            "User Full Name *Anonymized": "User_ID"
        }
        self.stats: Dict[str, Dict[str, int]] = {}
        self.processed_files: Set[str] = set()
        self._ensure_backup_path()
        self._load_state()

    def _ensure_backup_path(self) -> None:
        self.backup_file_path.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> None:
        try:
            if self.state_file.exists():
                with self.state_file.open('r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.data = state.get('data', {})
                    self.stats = state.get('stats', {})
                    self.processed_files = set(state.get('processed_files', []))
                    self.excluded_components = set(state.get('excluded_components', 
                                                          {'System', 'Folder'}))
                print("Previous state loaded successfully")
        except Exception as e:
            print(f"Error loading state: {str(e)}")
            self._initialize_new_state()

    def _initialize_new_state(self) -> None:
        self.data = {}
        self.stats = {}
        self.processed_files = set()
        self._save_state()

    def _save_state(self) -> None:
        try:
            state = {
                'stats': self.stats,
                'processed_files': list(self.processed_files),
                'excluded_components': list(self.excluded_components),
                'last_updated': datetime.now().isoformat(),
                'data': self.data
            }
            
            with self.state_file.open('w', encoding='utf-8') as f:
                json.dump(state, f, indent=4)
                
        except Exception as e:
            print(f"Error saving state: {str(e)}")

    def _clean_csv_data(self, file_path: Path) -> pd.DataFrame:
        """
        Clean and validate CSV data before processing
        """
        try:
            # Read CSV with more robust error handling
            df = pd.read_csv(
                file_path,
                encoding='utf-8',
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'NaN'],
                dtype_backend='numpy_nullable'
            )
            
            # Drop completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = df.columns.str.strip().str.replace(' +', ' ')
            
            # Handle missing values based on column type
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Fill missing text values with 'Unknown'
                    df[col] = df[col].fillna('Unknown')
                else:
                    # Fill missing numeric values with 0
                    df[col] = df[col].fillna(0)
            
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Sort DataFrame by any date column if it exists
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                df = df.sort_values(date_cols[0])
            
            return df
        
        except Exception as e:
            raise Exception(f"Error cleaning CSV data: {str(e)}")

    def process_csv_files(self, *file_paths: str) -> None:
        """
        Process CSV files and save them as JSON.
        Only handles the initial CSV processing and JSON conversion.
        """
        newly_processed = False
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                
                if str(path) in self.processed_files:
                    print(f"Skipping already processed file: {path}")
                    continue
                    
                dataset_name = path.stem.upper()  # Normalize dataset names
                
                # Clean and validate the data
                df = self._clean_csv_data(path)
                
                # Convert DataFrame to list of dictionaries for JSON storage
                records = df.to_dict('records')
                
                total_rows = len(records)
                
                # Store statistics with original row count
                self.stats[dataset_name] = {
                    'total_rows': total_rows,
                    'original_rows': total_rows,  # Add this line explicitly
                    'processed_at': datetime.now().isoformat()
                }
                
                self.data[dataset_name] = records
                self.processed_files.add(str(path))
                newly_processed = True
                
                print(f"Successfully processed {dataset_name}")
                print(f"Total rows: {total_rows}")
                
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
                continue
        
        if newly_processed:
            self._save_json_records()
            self._save_state()

    def remove_excluded_components(self) -> None:
        """
        Filter out records with excluded components from the JSON data.
        Updates statistics after filtering.
        """
        try:
            for dataset_name, records in self.data.items():
                # Get original row count or use total rows as fallback
                original_rows = self.stats[dataset_name].get('original_rows', 
                                                        self.stats[dataset_name].get('total_rows', 0))
                
                # Filter out excluded components
                filtered_records = [
                    record for record in records 
                    if record.get('Component') not in self.excluded_components
                ]
                
                # Update statistics
                filtered_rows = len(filtered_records)
                self.stats[dataset_name].update({
                    'filtered_rows': filtered_rows,
                    'removed_rows': original_rows - filtered_rows,
                    'filtered_at': datetime.now().isoformat()
                })
                
                # Update data with filtered records
                self.data[dataset_name] = filtered_records
                
                print(f"\nFiltering results for {dataset_name}:")
                print(f"Original rows: {original_rows}")
                print(f"Rows after filtering: {filtered_rows}")
                print(f"Removed rows: {original_rows - filtered_rows}")
                
            # Save updated state
            self._save_state()
            
        except Exception as e:
            raise Exception(f"Error removing excluded components: {str(e)}")
        
    def rename_user_column(self) -> None:
        """
        Rename 'User Full Name *Anonymized' column to 'User_ID' in all datasets.
        """
        try:
            old_key = "User Full Name *Anonymized"
            new_key = "User_ID"
            
            for dataset_name, records in self.data.items():
                # Rename column in each record
                for record in records:
                    if old_key in record:
                        record[new_key] = record.pop(old_key)
                
                print(f"Renamed user column in {dataset_name}")
            
            # Save updated state
            self._save_json_records()
            self._save_state()
            
        except Exception as e:
            raise Exception(f"Error renaming user column: {str(e)}")


    def _save_json_records(self) -> None:
            """
            Save processed records to JSON with enhanced metadata
            """
            if not self.data:
                print("No data to save")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file_path = self.backup_file_path / f"processed_data_{timestamp}.json"
            
            metadata = {
                'processed_at': timestamp,
                'file_statistics': self.stats,
                'processed_files': list(self.processed_files),
                'excluded_components': list(self.excluded_components),
                'column_mappings': self.column_mappings
            }
            
            output_data = {
                'metadata': metadata,
                'data': self.data
            }
            
            try:
                with json_file_path.open('w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=4)
                print(f"\nJSON records saved to: {json_file_path}")
                
            except Exception as e:
                raise Exception(f"Error saving JSON records: {str(e)}")

    def _rename_columns(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rename columns according to mapping with error handling
        """
        try:
            return {
                self.column_mappings.get(key, key): value
                for key, value in row.items()
            }
        except Exception as e:
            raise Exception(f"Error renaming columns: {str(e)}")

    def merge_datasets(self) -> pd.DataFrame:
        try:
            required_datasets = {'ACTIVITY_LOG', 'USER_LOG'}
            available_datasets = set(self.data.keys())
            
            if not required_datasets.issubset(available_datasets):
                missing = required_datasets - available_datasets
                raise ValueError(f"Missing required datasets: {missing}")
            
            activity_df = pd.DataFrame(self.data['ACTIVITY_LOG'])
            user_df = pd.DataFrame(self.data['USER_LOG'])
            component_df = pd.DataFrame(self.data['COMPONENT_CODES'])
            
            merged_df = pd.concat([
                activity_df.reset_index(),
                user_df.reset_index()
            ], axis=1)
            
            merged_df = merged_df.merge(
                component_df,
                on='Component',
                how='left'
            )

            # Remove the first column (duplicate index)
            merged_df = merged_df.iloc[:, 2:]
            
            merged_df['Month'] = pd.to_datetime(merged_df['Date']).dt.strftime('%Y-%m')
            
            return merged_df
            
        except Exception as e:
            raise Exception(f"Merge operation failed: {str(e)}")

    def reshape_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reshape merged data using pivot operation with enhanced features
        """
        try:
            # Convert User_ID to integer type
            df['User_ID'] = df['User_ID'].astype(int)

            
            # Create pivot table
            pivot_df = pd.pivot_table(
                df,
                index=['User_ID', 'Month'],
                columns=['Component'],
                values='Action',
                aggfunc='count',
                fill_value=0
            )
            
            # Reset index for easier handling
            pivot_df = pivot_df.reset_index()
            
            # Add total interactions column
            activity_cols = [col for col in pivot_df.columns if col not in ['User_ID', 'Month']]
            pivot_df['Total_Interactions'] = pivot_df[activity_cols].sum(axis=1)
            
            # Sort by User_ID numerically and then by Month
            pivot_df = pivot_df.sort_values(['User_ID', 'Month'])
            
            return pivot_df
                
        except Exception as e:
            raise Exception(f"Reshape operation failed: {str(e)}")

    def count_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            interaction_counts = df.groupby(
                ['User_ID', 'Component', 'Month']
            ).size().reset_index(name='Interaction_Count')
            
            return interaction_counts
            
        except Exception as e:
            raise Exception(f"Counting interactions failed: {str(e)}")

    def get_data(self, dataset_name: str = None) -> Dict[str, List[Dict[str, Any]]]:
        if dataset_name:
            return {dataset_name: self.data.get(dataset_name, [])}
        return self.data

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            'processed_files': len(self.processed_files),
            'total_records': sum(len(records) for records in self.data.values()),
            'datasets': list(self.data.keys()),
            'last_updated': self.stats.get('last_updated', 'Never')
        }

    def clear_state(self) -> None:
        self._initialize_new_state()
        print("Application state cleared")