import pandas as pd


class ExcelDataProcessor:
    def __init__(self, file_path="data/input1.xlsx",output_path="data/GAMS/input.xlsx"):
        self.file_path = file_path
        self.col=[]
        for i in range(96):
            self.col.append(i+1)
        self.file_path = file_path
        self.output_path =output_path

    def get_gen_info(self):
        """
        Reads the 'GEN_INFO' sheet from the Excel file, processes the data by setting
        the correct column headers, removing unnecessary rows, and dropping specific columns.

        Returns:
            pd.DataFrame: The processed DataFrame containing general information.
        """
        # Load the "GEN_INFO" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="GEN_INFO")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1]

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the column labeled "Sl/no", as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned and processed DataFrame
        return df

    def get_discom_share_for_generation(self):
        """
        Processes the 'GEN_DISCOM_SHARE' sheet from the Excel file to transform and filter
        discom share data, replacing NaN values with zero, and reshaping the DataFrame.

        Returns:
            pd.DataFrame: The processed DataFrame containing discom shares with non-zero values.
        """
        # Load the "GEN_DISCOM_SHARE" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="GEN_DISCOM_SHARE",skiprows=2)

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Replace all NaN values with 0 to handle missing data
        df.fillna(0, inplace=True)

        # Identify columns to melt, excluding the 'Generator_Name' column
        col_to_melt = df.columns.drop('Generator_Name')

        # Reshape the DataFrame from wide to long format
        df = pd.melt(
            df,
            id_vars=['Generator_Name'],
            value_vars=col_to_melt,
            var_name='Discom_Name',
            value_name='Share'
        )

        # Filter rows where the 'Share' value is greater than 0
        df = df[df['Share'] > 0]

        # Return the processed DataFrame
        return df

    def get_oa_availability(self):
        """
        Reads and processes the 'OA_AVAILABILITY_DATA' sheet from the Excel file,
        setting appropriate column headers, removing unnecessary rows, and dropping specific columns.

        Returns:
            pd.DataFrame: The processed DataFrame containing OA availability data.
        """
        # Load the "OA_AVAILABILITY_DATA" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="OA_AVAILABILITY_DATA")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned and processed DataFrame
        return df

    def get_date_revision(self):
        # Read Excel
        rev_df = pd.read_excel(
            self.file_path,
            sheet_name="GEN_DC_DATA"
        )

        # Extract values
        date = rev_df.columns[1]  # second column header
        revision = rev_df.iloc[0, 1]  # first row, second column value

        # Return DataFrame with proper structure
        return pd.DataFrame({
            "date": [date],
            "revision": [revision]
        })

    def get_dc_of_intra(self):
        """
        Processes the 'GEN_DC_DATA' sheet from the Excel file to extract and adjust
        intra-state generation data, using the discom share to calculate specific values.

        Returns:
            pd.DataFrame: The merged and adjusted DataFrame with generation data.
        """
        # Load the "GEN_DC_DATA" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="GEN_DC_DATA")

        # Copy the third row (index 2) to use as column names
        col = df.iloc[1].copy()

        # Set the first two entries in the column names: 'Sl/no' and 'Generator_Name'
        col.iloc[0] = "Sl/no"
        col.iloc[1] = "Generator_Name"

        # Convert remaining column names to integers, assuming these are time intervals or specific identifiers
        col.iloc[2:] = col.iloc[2:].astype(int)

        # Assign the new column names to the DataFrame
        df.columns = col

        # Remove the first three rows, which contain meta-information or are not part of the actual data
        df = df.iloc[3:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Obtain the discom share DataFrame from the function `get_discom_share_for_generation`
        df_share = self.get_discom_share_for_generation()

        # Merge the discom share data with the generation data on the "Generator_Name" column
        df_merge = pd.merge(df_share, df, on="Generator_Name")

        # Identify the columns that contain numerical values to adjust by share percentage
        col1 = col.iloc[2:]

        # Adjust the merged DataFrame's relevant columns by multiplying with 'Share' and dividing by 100
        df_merge[col1] = df_merge[col1].mul(df_merge['Share'], axis=0) / 100

        # Return the merged and adjusted DataFrame
        return df_merge

    def get_gen_discomwise_dc_with_mod_column(self):
        """
        Processes intra-state generation data by merging discom share and additional generator info,
        including MOD rates and applicability.

        Returns:
            pd.DataFrame: The merged DataFrame containing generation data with MOD rates and applicability.
        """
        # Get the intra-state generation data merged with discom share from the `get_dc_of_intra` function
        df = self.get_dc_of_intra()

        # Retrieve additional generator information from the `get_gen_info` function
        df_info = self.get_gen_info()

        # Select the relevant columns from the generator information DataFrame
        df_info = df_info[['Generator_Name', 'InsgsType', 'MOD_Rate', 'MOD_Applicability']]

        # Merge the intra-state generation data with the additional generator info on "Generator_Name"
        df = pd.merge( df_info, df, on="Generator_Name")

        # Return the merged DataFrame containing generation data along with MOD rates and applicability
        return df

    def get_gen_without_hydro(self):
        # Retrieve the dataframe by calling the method get_gen_discomwise_dc_with_mod_column()
        df = self.get_gen_discomwise_dc_with_mod_column()

        # Filter out rows where 'InsgsType' is "HYDRO" to exclude hydro generation data
        df = df[~(df['InsgsType'] == "HYDRO")]

        #
        df['InsgsType']=df['Discom_Name']
        df=df.drop(columns="Discom_Name")
        df=df.rename(columns={"InsgsType":"Discom_Name"})

        # Return the filtered dataframe that excludes hydro generation
        return df

    def get_hydro_gen(self):
        # Retrieve the dataframe by calling the method get_gen_discomwise_dc_with_mod_column()
        df = self.get_gen_discomwise_dc_with_mod_column()

        # Filter the dataframe to include only rows where 'InsgsType' is "HYDRO", isolating hydro generation data
        df = df[(df['InsgsType'] == "HYDRO")]

        # Return the filtered dataframe that includes only hydro generation
        return df

    def get_hydro_schedule(self):

        df=self.get_hydro_gen()

        dfs=pd.read_excel(self.file_path,sheet_name="GEN_SCH_DETAILS")
        dfs.columns=dfs.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)
        dfs=dfs.drop(columns='Sl/no')
        dfs=dfs.iloc[2:]
        df_merge=pd.merge(df[["Generator_Name","InsgsType","MOD_Rate","MOD_Applicability","Discom_Name","Share"]],dfs[~(dfs['Discom_Name']=="VSE")],on=["Generator_Name","Discom_Name"])

        return df_merge

    def get_hydro_requization(self):

        df=self.get_hydro_gen()

        dfs=pd.read_excel(self.file_path,sheet_name="DISCOM_HYDRO_REQ_DETAILS")
        dfs.columns=dfs.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)
        dfs=dfs.drop(columns='Sl/no')
        dfs=dfs.iloc[2:]
        df_merge=pd.merge(df[["Generator_Name","InsgsType","MOD_Rate","MOD_Applicability","Discom_Name","Share"]],dfs[~(dfs['Discom_Name']=="VSE")],on=["Generator_Name","Discom_Name"])

        return df_merge


    def get_center_share(self):
        """
        Reads and processes the 'CENTRE' sheet from the Excel file to calculate the Center share
        discom-wise, and adds a row representing the total Center share.

        Returns:
            pd.DataFrame: The processed DataFrame containing Center share data discom-wise,
                          with a row showing the total Center share.
        """
        # Load the "CENTRE" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="CENTRE")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Ensure the "Generator_Name" column is treated as an object type (string)
        df["Generator_Name"] = df["Generator_Name"].astype(object)

        # Replace rows where "Generator_Name" is "Power_Exchange" with "Centre"
        df.loc[df["Generator_Name"] == "Power_Exchange", "Generator_Name"] = "Centre"

        # Group the DataFrame by "Discom_Name" and sum the values for each group
        df_group = df.groupby(by="Discom_Name").sum()

        # Reset the index to convert the grouped data back to a standard DataFrame format
        df_group.reset_index(inplace=True)

        # Add a row labeled "Total" under "Generator_Name" for rows where "Discom_Name" is "Power_Exchange"
        df_group.loc[df_group["Discom_Name"] == "Power_Exchange", "Generator_Name"] = "Extra"

        # Return the processed DataFrame
        return df_group

    def get_px(self):
        """
        Reads and processes the 'PX' sheet from the Excel file to calculate the Power Exchange
        data discom-wise, and adds a row representing the total share.

        Returns:
            pd.DataFrame: The processed DataFrame containing Power Exchange data discom-wise,
                          with a row showing the total share for Power Exchange.
        """
        # Load the "PX" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="PX")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Ensure the "Generator_Name" column is treated as an object type (string)
        df["Generator_Name"] = df["Generator_Name"].astype(object)

        # Replace rows where "Discom_Name" is not "Power_Exchange" with "Power_Exchange" for "Generator_Name"
        df.loc[df["Discom_Name"] != "Power_Exchange", "Generator_Name"] = "Power_Exchange"

        # Group the DataFrame by "Discom_Name" and sum the values for each group
        df_group = df.groupby(by="Discom_Name").sum()

        # Reset the index to convert the grouped data back to a standard DataFrame format
        df_group.reset_index(inplace=True)

        # Add a row labeled "Total" under "Generator_Name" for rows where "Discom_Name" is "Power_Exchange"
        df_group.loc[df_group["Discom_Name"] == "Power_Exchange", "Generator_Name"] = "Power_Exchange"
        df_group.loc[df_group["Discom_Name"] == "Power_Exchange", "Discom_Name"] = "Extra"

        # Return the processed DataFrame
        return df_group

    def get_rtm(self):
        """
        Reads and processes the 'RTM' sheet from the Excel file to calculate the
        Real-Time Market (RTM) data discom-wise, and adds a row representing the total share.

        Returns:
            pd.DataFrame: The processed DataFrame containing RTM data discom-wise,
                          with a row showing the total RTM share.
        """
        # Load the "RTM" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="RTM")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Group the DataFrame by "Discom_Name" and sum the values for each group
        df_group = df.groupby(by="Discom_Name").sum()

        # Reset the index to convert the grouped data back to a standard DataFrame format
        df_group.reset_index(inplace=True)

        # Correct the row labeled "Total" under "Generator_Name" for rows where "Discom_Name" is "RTM"
        df_group.loc[df_group["Discom_Name"] == "RTM", "Generator_Name"] = "RTM"
        df_group.loc[df_group["Discom_Name"] == "RTM", "Discom_Name"] = "Extra"

        # Return the processed DataFrame
        return df_group

    def get_remc(self):
        """
        Reads and processes the 'REMC' sheet from the Excel file by setting appropriate column headers,
        removing unnecessary rows and columns, and resetting the index.

        Returns:
            pd.DataFrame: The processed DataFrame containing REMC data.
        """
        # Load the "REMC" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="REMC")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Reset the index to ensure it starts from 0 after rows removal
        df.reset_index(drop=True, inplace=True)

        # Return the processed DataFrame
        return df

    def get_intra_discom(self):
        """
        Reads and processes the 'INTRA_DISCOM_TRADE' sheet from the Excel file by setting appropriate
        column headers, removing unnecessary rows and columns, and resetting the index.

        Returns:
            pd.DataFrame: The processed DataFrame containing intra-discom trade data.
        """
        # Load the "INTRA_DISCOM_TRADE" sheet from the Excel file into a DataFrame
        df = pd.read_excel(self.file_path, sheet_name="INTRA_DISCOM_TRADE")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, which are not part of the actual data
        df = df.iloc[2:]

        # Drop the "Sl/no" column, as it is not needed
        df.drop(columns="Sl/no", inplace=True)

        # Reset the index to ensure it starts from 0 after rows removal
        df.reset_index(drop=True, inplace=True)

        # Return the processed DataFrame
        return df

    def get_discom_demand(self):
        # Read the Excel file into a DataFrame, selecting the sheet named "DISCOM_DRAWAL_SCH_DATA"
        df = pd.read_excel(self.file_path, sheet_name="DISCOM_DRAWAL_SCH_DATA")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, as they are headers or metadata, not part of the actual data
        df = df.iloc[2:]

        # Drop the column named "Sl/no" as it's not needed for the data analysis
        df.drop(columns="Sl/no", inplace=True)

        # Reset the index of the DataFrame to start from 0 after removing the unnecessary rows
        df.reset_index(drop=True, inplace=True)

        return df


    def get_discom_demand2(self):
        # Read the Excel file into a DataFrame, selecting the sheet named "DISCOM_DRAWAL_SCH_DATA"
        df = pd.read_excel(self.file_path, sheet_name="DISCOM_TARGETINJ_SCH_DATA")

        # Set the column headers to the second row (index 1) of the DataFrame
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Remove the first two rows, as they are headers or metadata, not part of the actual data
        df = df.iloc[2:]

        # Drop the column named "Sl/no" as it's not needed for the data analysis
        df.drop(columns="Sl/no", inplace=True)

        # Reset the index of the DataFrame to start from 0 after removing the unnecessary rows
        df.reset_index(drop=True, inplace=True)

        return df

    def mod_demand(self):
        col=self.col
        demand=self.get_discom_demand2()
        demand = demand.set_index("Discom_Name")
        px = self.get_px().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        remc = self.get_remc().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        rtm = self.get_rtm().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        centre = self.get_center_share().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        intra_discom = self.get_intra_discom().set_index("Discom_Name").reindex(demand.index, fill_value=0)

        # Calculate MOD demand
        mod_demand = demand.copy()
        mod_demand[col] = demand[col] - px[col] - remc[col] - rtm[col] - centre[col] - intra_discom[col]
        return mod_demand

    def get_ramp_up(self):
        # Read the "GEN_RAMP_UP_DATA" sheet from the Excel file located at self.file_path
        df = pd.read_excel(self.file_path, sheet_name="GEN_RAMP_UP_DATA")

        # Set the column names using the second row of the dataframe, converting any float type columns to int
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Skip the first two rows of the dataframe as they are not part of the actual data
        df = df.iloc[2:]

        # Fill any missing values in the 'Approval_No' column with the default value "Intra_State_Generation"
        df['Approval_No'] = df['Approval_No'].fillna("Intra_State_Generation")

        # Drop the "Sl/no" column from the dataframe as it is not required
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned dataframe
        return df

    def get_ramp_down(self):
        # Read the "GEN_RAMP_DOWN_DATA" sheet from the Excel file located at self.file_path
        df = pd.read_excel(self.file_path, sheet_name="GEN_RAMP_DOWN_DATA")

        # Set the column names using the second row of the dataframe, converting any float type columns to int
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Skip the first two rows of the dataframe as they are not part of the actual data
        df = df.iloc[2:]

        # Fill any missing values in the 'Approval_No' column with the default value "Intra_State_Generation"
        df['Approval_No'] = df['Approval_No'].fillna("Intra_State_Generation")

        # Drop the "Sl/no" column from the dataframe as it is not required
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned dataframe
        return df


    def get_pmax(self):
        # Read the "GEN_Pmax_DATA" sheet from the Excel file located at self.file_path
        df = pd.read_excel(self.file_path, sheet_name="GEN_Pmax_DATA")

        # Set the column names using the second row of the dataframe, converting any float type columns to int
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Skip the first two rows of the dataframe as they are not part of the actual data
        df = df.iloc[2:]

        # Fill any missing values in the 'Approval_No' column with the default value "Intra_State_Generation"
        df['Approval_No'] = df['Approval_No'].fillna("Intra_State_Generation")

        # Drop the "Sl/no" column from the dataframe as it is not required
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned dataframe
        return df


    def get_pmin(self):
        # Read the "GEN_Pmin_DATA" sheet from the Excel file located at self.file_path
        df = pd.read_excel(self.file_path, sheet_name="GEN_Pmin_DATA")

        # Set the column names using the second row of the dataframe, converting any float type columns to int
        df.columns = df.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)

        # Skip the first two rows of the dataframe as they are not part of the actual data
        df = df.iloc[2:]

        # Fill any missing values in the 'Approval_No' column with the default value "Intra_State_Generation"
        df['Approval_No'] = df['Approval_No'].fillna("Intra_State_Generation")

        # Drop the "Sl/no" column from the dataframe as it is not required
        df.drop(columns="Sl/no", inplace=True)

        # Return the cleaned dataframe
        return df


    def get_schedule(self):



        dfs=pd.read_excel(self.file_path,sheet_name="GEN_SCH_DETAILS", engine='openpyxl')
        dfs.columns=dfs.iloc[1].apply(lambda x: int(x) if isinstance(x, float) else x)
        dfs=dfs.drop(columns='Sl/no')
        dfs=dfs.iloc[2:]

        return dfs

    def get_demand_left(self):
        """
        Processes the data to calculate the MOD demand by subtracting various
        components like PX, REMC, RTM, Centre, Intra Discom, and Must Run
        from the total demand.

        Returns:
            pd.DataFrame: The DataFrame containing the calculated MOD demand.
        """
        # Get demand data
        demand = self.get_discom_demand2()
        demand = demand.set_index("Discom_Name")

        # Get intra data without hydro and separate MOD and Must Run
        intra = self.get_gen_without_hydro()
        mod = intra[intra['MOD_Applicability'] == 1]
        must = intra[intra['MOD_Applicability'] == 0]
        must_run = must.groupby(by="Discom_Name").sum()

        # Align must_run with demand index
        col = demand.columns
        must_run = must_run[col]
        must_run = must_run.reindex(demand.index, fill_value=0)

        # Get OA availability and separate MOD and Must OA Run
        oa = self.get_oa_availability()
        mod_oa = oa[oa['MOD_Applicability'] == 1]
        must_oa = oa[oa['MOD_Applicability'] == 0]
        must_oa_run = must_oa.groupby(by="Discom_Name").sum()

        # Align must_oa_run with demand index
        must_oa_run = must_oa_run[col]
        must_oa_run = must_oa_run.reindex(demand.index, fill_value=0)

        # Get and reindex other components
        px = self.get_px().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        remc = self.get_remc().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        rtm = self.get_rtm().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        centre = self.get_center_share().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        intra_discom = self.get_intra_discom().set_index("Discom_Name").reindex(demand.index, fill_value=0)

        # Calculate MOD demand
        mod_demand = demand.copy()
        mod_demand[col] = demand[col] - px[col] - remc[col] - rtm[col] - centre[col] - intra_discom[col]

        # Return the MOD demand DataFrame with calculated values
        return mod_demand[col].astype(int)

    def get_must_run_intra_gen(self):
        intra = self.get_gen_without_hydro()
        demand = self.get_discom_demand2()
        mod = intra[intra['MOD_Applicability'] == 1]
        must = intra[intra['MOD_Applicability'] == 0]

        gen_info = self.get_gen_info()
        must_run = pd.merge(gen_info, must, on="Generator_Name")

        return must_run


    def get_must_run_oa(self):
        oa = self.get_oa_availability()
        demand = self.get_discom_demand2()
        demand = demand.set_index("Discom_Name")
        mod_oa = oa[oa['MOD_Applicability'] == 1]
        must_oa = oa[oa['MOD_Applicability'] == 0]


        # Align must_oa_run with demand index


        return must_oa

    def get_demand_for_mod(self):
        """
        Processes the data to calculate the MOD demand by subtracting various
        components like PX, REMC, RTM, Centre, Intra Discom, and Must Run
        from the total demand.

        Returns:
            pd.DataFrame: The DataFrame containing the calculated MOD demand.
        """
        # Get demand data
        demand = self.get_discom_demand2()
        demand = demand.set_index("Discom_Name")

        # Get intra data without hydro and separate MOD and Must Run
        intra = self.get_gen_without_hydro()
        mod = intra[intra['MOD_Applicability'] == 1]
        must = intra[intra['MOD_Applicability'] == 0]
        #

        # Align must_run with demand index
        col = demand.columns

        gen_info=self.get_gen_info()

        # must_run=pd.merge(gen_info,must,on="Generator_Name")

        must_run = must.groupby(by="Discom_Name").sum()

        must_run = must_run.reindex(demand.index, fill_value=0)
        must_run = must_run[col]

        # Get OA availability and separate MOD and Must OA Run
        oa = self.get_oa_availability()
        mod_oa = oa[oa['MOD_Applicability'] == 1]
        must_oa = oa[oa['MOD_Applicability'] == 0]
        must_oa_run = must_oa.groupby(by="Discom_Name").sum()

        # Align must_oa_run with demand index
        must_oa_run = must_oa_run[col]
        must_oa_run = must_oa_run.reindex(demand.index, fill_value=0)

        # Get and reindex other components
        px = self.get_px().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        remc = self.get_remc().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        rtm = self.get_rtm().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        centre = self.get_center_share().set_index("Discom_Name").reindex(demand.index, fill_value=0)
        intra_discom = self.get_intra_discom().set_index("Discom_Name").reindex(demand.index, fill_value=0)

        # Calculate MOD demand
        mod_demand = demand.copy()
        mod_demand[col] = demand[col] - px[col] - remc[col] - rtm[col] - centre[col] - intra_discom[col] - must_run[
            col] - must_oa_run[col]

        # Return the MOD demand DataFrame with calculated values
        return mod_demand[col].astype(int)

    def get_pmin_generation(self, gen_type="all"):
        """
        Processes the data to calculate the MOD demand by subtracting various
        components like PX, REMC, RTM, Centre, Intra Discom, and Must Run
        from the total demand.

        Returns:
            pd.DataFrame: The DataFrame containing the calculated MOD demand.
        """


        # Retrieve Pmin and generator information
        pmin_data = self.get_pmin()
        generator_info = self.get_gen_info()

        # Filter Pmin data for intra-state generation and merge with generator information
        pmin_intra_state = pmin_data[pmin_data['Approval_No'] == "Intra_State_Generation"]
        pmin_intra_state = pd.merge(pmin_intra_state, generator_info, on="Generator_Name")

        # Fetch discom share for generation
        discom_share = self.get_discom_share_for_generation()

        # Apply MOD applicability filter if specified
        if gen_type == "mod":
            pmin_intra_state = pmin_intra_state[pmin_intra_state['MOD_Applicability'] == 1]
        elif gen_type == "must":
            pmin_intra_state = pmin_intra_state[pmin_intra_state['MOD_Applicability'] == 0]

        # Merge discom share data with filtered Pmin intra-state data
        generation_data = pd.merge(discom_share, pmin_intra_state, on="Generator_Name")

        # Scale generation data by share percentages
        for i in range(96):
            generation_data[i + 1] = generation_data[i + 1] * generation_data['Share'] / 100

        # Group by discom name and sum the generation values
        return generation_data



    def get_pmin_intra_total(self,type="all"):
        generation_data=self.get_pmin_generation(type)
        #get Pmin of Intra Generation
        demand = self.get_discom_demand2().set_index("Discom_Name")
        generation_summary = generation_data.groupby("Discom_Name").sum()

        # Reindex the summary to match the demand index and fill missing values with zeros
        generation_summary = generation_summary[self.col].reindex(demand.index, fill_value=0)

        return generation_summary

    def get_pmin_of_OA_generation(self,type="all"):
        oa=self.get_oa_availability()
        oa = oa[['Generator_Name', 'Discom_Name', 'OA_Type', 'Approval_No', 'MOD_Rate', 'MOD_Applicability']]
        pmin=self.get_pmin()
        pmin_oa = pd.merge(oa, pmin, on=["Generator_Name", "Approval_No"])
        if(type=="mod"):
            pmin_oa=pmin_oa[pmin_oa['MOD_Applicability']==1]
        if (type == "must"):
            pmin_oa = pmin_oa[pmin_oa['MOD_Applicability'] == 0]
        return pmin_oa

    def get_pmin_oa_total(self,type="all"):
        oa=self.get_pmin_of_OA_generation(type)
        demand = self.get_discom_demand2().set_index("Discom_Name")

        summary=oa.groupby("Discom_Name").sum();
        summary = summary[self.col].reindex(demand.index, fill_value=0)

        return summary


    def get_pmax_intra(self,type="all"):
        pmax=self.get_pmax()
        pmax=pmax[pmax['Approval_No']=="Intra_State_Generation"]
        gen=self.get_gen_discomwise_dc_with_mod_column()
        gen=gen[['Generator_Name','InsgsType','MOD_Rate','MOD_Applicability','Discom_Name','Share']]
        gen_data=pd.merge(gen,pmax,on="Generator_Name")
        for i in  range(96):
            gen_data[i+1]=gen_data[i+1]*gen_data['Share']/100

        if type=="mod":
            gen_data=gen_data[gen_data['MOD_Applicability']==1]
        if type=="must":
            gen_data=gen_data[gen_data['MOD_Applicability']==0]

        gen_data=gen_data[["Generator_Name","Discom_Name","MOD_Rate","MOD_Applicability","Share"]+self.col]

        return gen_data

    def get_pmax_of_OA_generation(self,type="all"):
        oa=self.get_oa_availability()
        oa = oa[['Generator_Name', 'Discom_Name', 'OA_Type', 'Approval_No', 'MOD_Rate', 'MOD_Applicability']]
        pmax=self.get_pmax()
        pmax_oa = pd.merge(oa, pmax, on=["Generator_Name", "Approval_No"])
        if(type=="mod"):
            pmax_oa=pmax_oa[pmax_oa['MOD_Applicability']==1]
        if (type == "must"):
            pmax_oa = pmax_oa[pmax_oa['MOD_Applicability'] == 0]
        return pmax_oa


    def get_rampup_intra(self,type="all"):
        rampup=self.get_ramp_up()
        rampup=rampup[rampup['Approval_No']=="Intra_State_Generation"]
        gen=self.get_gen_discomwise_dc_with_mod_column()
        gen=gen[['Generator_Name','InsgsType','MOD_Rate','MOD_Applicability','Discom_Name','Share']]
        gen_data=pd.merge(gen,rampup,on="Generator_Name")
        for i in  range(96):
            gen_data[i+1]=gen_data[i+1]*gen_data['Share']/100

        if type=="mod":
            gen_data=gen_data[gen_data['MOD_Applicability']==1]
        if type=="must":
            gen_data=gen_data[gen_data['MOD_Applicability']==0]


        return gen_data

    def get_rampup_of_OA_generation(self,type="all"):
        oa=self.get_oa_availability()
        oa = oa[['Generator_Name', 'Discom_Name', 'OA_Type', 'Approval_No', 'MOD_Rate', 'MOD_Applicability']]
        rampup=self.get_ramp_up()
        rampup_oa = pd.merge(oa, rampup, on=["Generator_Name", "Approval_No"])
        if(type=="mod"):
            rampup_oa=rampup_oa[rampup_oa['MOD_Applicability']==1]
        if (type == "must"):
            rampup_oa = rampup_oa[rampup_oa['MOD_Applicability'] == 0]
        rampup=rampup_oa.groupby('Generator_Name').first()
        return rampup


    def get_rampdown_intra(self,type="all"):
        rampdown=self.get_ramp_down()
        rampdown=rampdown[rampdown['Approval_No']=="Intra_State_Generation"]
        gen=self.get_gen_discomwise_dc_with_mod_column()
        gen=gen[['Generator_Name','InsgsType','MOD_Rate','MOD_Applicability','Discom_Name','Share']]
        gen_data=pd.merge(gen,rampdown,on="Generator_Name")
        for i in  range(96):
            gen_data[i+1]=gen_data[i+1]*gen_data['Share']/100

        if type=="mod":
            gen_data=gen_data[gen_data['MOD_Applicability']==1]
        if type=="must":
            gen_data=gen_data[gen_data['MOD_Applicability']==0]
        return gen_data


    def get_rampdown_of_OA_generation(self,type="all"):
        oa=self.get_oa_availability()
        oa = oa[['Generator_Name', 'Discom_Name', 'OA_Type', 'Approval_No', 'MOD_Rate', 'MOD_Applicability']]
        rampdown=self.get_ramp_down()
        rampdown_oa = pd.merge(oa, rampdown, on=["Generator_Name", "Approval_No"])
        if(type=="mod"):
            rampdown_oa=rampdown_oa[rampdown_oa['MOD_Applicability']==1]
        if (type == "must"):
            rampdown_oa = rampdown_oa[rampdown_oa['MOD_Applicability'] == 0]
        rampdown=rampdown_oa.groupby('Generator_Name').first()
        return rampdown



    def get_intra_mod_schedule(self,type="all"):
        df=self.get_schedule()
        df=df[df['Schedule_Type']=="Intra State Generation"].drop(columns="Approval_No")
        # df=df.groupby(by="Discom_Name").sum()

        gen=self.get_gen_info()
        df=pd.merge(gen,df,on="Generator_Name")
        if type=="mod":
            df=df[df['MOD_Applicability']==1]
        if type=="must":
            df = df[df['MOD_Applicability'] == 0]
        return df

    def get_intra_mod_schedule_total(self,type="all"):
        df=self.get_intra_mod_schedule(type);
        df=df.groupby("Discom_Name").sum()
        return df[self.col]

    def get_oa_schedule(self):
        df=self.get_schedule()
        df=df[df['Schedule_Type'].isin(['STOA','LTOA','MTOA'])]
        print(df['Schedule_Type'].unique())
        df=df.groupby(by="Discom_Name").sum()

        return df[self.col]



    def get_mod_oa_schedule(self,type="all"):
        df = self.get_schedule()
        df = df[df['Schedule_Type'].isin(['STOA', 'LTOA', 'MTOA'])]

        gen = self.get_oa_availability()[['Generator_Name','Discom_Name','MOD_Applicability','MOD_Rate','Approval_No']]
        df = pd.merge(gen, df, on=["Generator_Name","Approval_No","Discom_Name"])
        if type == "mod":
            df = df[df['MOD_Applicability'] == 1]
        if type == "must":
            df = df[df['MOD_Applicability'] == 0]
        return df

    def createGAMSfile(self):
        info = pd.read_excel(self.file_path, sheet_name="GEN_INFO", skiprows=2)
        gen_info1 = pd.read_excel(self.file_path, sheet_name="OA_REQUISITION_DATA", skiprows=2)

        # In[3]:

        gen_share = pd.read_excel(self.file_path, sheet_name="GEN_DISCOM_SHARE",skiprows=2)
        gen_share = gen_share.fillna(0).drop(columns="Sl/no")
        col_to_melt = gen_share.columns.drop('Generator_Name')
        gen_share = pd.melt(
            gen_share,
            id_vars=['Generator_Name'],
            value_vars=col_to_melt,
            var_name='Discom_Name',
            value_name='Share'
        )
        gen_share = gen_share[~(gen_share['Share'] == 0)]

        # In[4]:

        gen_info = info.copy()
        gen_info1 = gen_info1[['Generator_Name', 'Discom_Name', 'Approval_No', 'MOD_Rate', 'MOD_Applicability']]
        gen_info1['InsgsType'] = "Open Access"
        gen_info1['Share'] = 100
        gen_info = gen_info[['Generator_Name', 'InsgsType', 'MOD_Rate', 'MOD_Applicability']]
        gen_info['Approval_No'] = "Intra State Generator"
        gen_info = pd.merge(gen_share, gen_info, on=["Generator_Name"], how="left")
        gen_info = pd.concat([gen_info, gen_info1])

        # In[5]:

        demand = pd.read_excel(self.file_path, sheet_name="DISCOM_TARGETINJ_SCH_DATA", skiprows=2).drop(
            columns="Sl/no").set_index("Discom_Name")
        center = pd.read_excel(self.file_path, sheet_name="CENTRE", skiprows=2).drop(columns="Sl/no").set_index(
            "Discom_Name")
        center = center[center['Generator_Name'] == "Power_Exchange"].drop(columns="Generator_Name")

        px = pd.read_excel(self.file_path, sheet_name="PX", skiprows=2).drop(columns="Sl/no")
        px = px[~(px['Discom_Name'] == "Power_Exchange")].drop(columns="Generator_Name").set_index("Discom_Name")

        rtm = pd.read_excel(self.file_path, sheet_name="RTM", skiprows=2).drop(columns="Sl/no")
        rtm = rtm[~(rtm['Discom_Name'] == "RTM")].drop(columns="Generator_Name").set_index("Discom_Name")

        remc = pd.read_excel(self.file_path, sheet_name="REMC", skiprows=2).drop(columns="Sl/no").set_index("Discom_Name")

        intra_discom = pd.read_excel(self.file_path, sheet_name="INTRA_DISCOM_TRADE", skiprows=2).drop(
            columns="Sl/no").set_index("Discom_Name")

        standby = pd.read_excel(self.file_path, sheet_name="STAND_BY", skiprows=2).drop(columns="Sl/no").set_index(
            "Discom_Name")

        # In[6]:

        # writer = pd.ExcelWriter('C:/Users/Khushboo/Documents/GAMS/Python/App1/notebook/GAMSData/input1.xlsx',engine='xlsxwriter')
        # gen_info.to_excel(writer, sheet_name="Info", index=False)
        # mod_demand.to_excel(writer, sheet_name="Demand", index=True)
        # pmax.to_excel(writer, sheet_name="Pmax", index=False)
        # pmin.to_excel(writer, sheet_name="Pmin", index=False)
        # hydro.to_excel(writer, sheet_name="Hydro", index=False)

        # In[7]:

        intra_demand = demand - center - px - rtm - remc - standby - intra_discom

        # In[8]:

        # writer.close()

        # In[9]:

        df = pd.read_excel(self.file_path, sheet_name="GEN_DC_DATA", skiprows=2)
        df = df.rename(columns={"Unnamed: 0": 'Sl/no', "Unnamed: 1": 'Generator_Name'})
        df = df.drop(columns="Sl/no")
        df1 = pd.merge(gen_share, df, on="Generator_Name", how="left")
        for i in range(1, 97):
            df1[i] = df1[i] * df1['Share'] / 100
        df1['Approval_No'] = "Intra State Generator"
        intra_pmax = pd.merge(gen_info, df1.drop(columns="Share"), on=["Generator_Name", "Discom_Name", "Approval_No"],
                              how="right")
        df2 = pd.read_excel(self.file_path, sheet_name="OA_REQUISITION_DATA", skiprows=2)
        intra_pmax = intra_pmax.drop(columns=["Share"])
        df2 = df2.drop(columns=["OA_Type", "Sl/no"])
        df2['InsgsType'] = "Open Access"
        pmax = pd.concat([intra_pmax, df2])
        pmax_mod = pmax[pmax['MOD_Applicability'] == 1]

        # In[10]:

        hydro = pmax[pmax['InsgsType'] == "HYDRO"]
        non_hydro = pmax[~(pmax['InsgsType'] == "HYDRO")]

        must = non_hydro[(non_hydro['MOD_Applicability'] == 0)]
        mustd = must.groupby(by="Discom_Name").sum()[list(range(1, 97))]

        # In[11]:

        mod = pd.read_excel(self.file_path, sheet_name="GEN_SCH_DETAILS", skiprows=2).drop(columns="Sl/no")
        mod = mod[mod['Schedule_Type'].isin(["Intra State Generation", "STOA", "MTOA", "LTOA"])]
        mod['Approval_No'] = mod['Approval_No'].fillna("Intra State Generator")
        col_of_interest = ['Generator_Name', 'Discom_Name', 'InsgsType',
                           'MOD_Rate', 'MOD_Applicability', 'Approval_No']
        sc = pd.merge(mod, non_hydro[col_of_interest], on=["Generator_Name", "Discom_Name", "Approval_No"])
        sc = sc[sc['MOD_Applicability'] == 1]

        scd = sc.groupby("Discom_Name").sum()[list(range(1, 97))]
        t1 = sc.groupby(by=["Generator_Name", "Discom_Name", "Approval_No"]).sum()[list(range(1, 97))]
        t2 = must.groupby(by=["Generator_Name", "Discom_Name", "Approval_No"]).sum()[list(range(1, 97))]


        # In[12]:

        hydro_sc = pd.merge(mod, hydro[col_of_interest], on=["Generator_Name", "Discom_Name", "Approval_No"])
        hydro_scd = hydro_sc.groupby(by="Discom_Name").sum()[list(range(1, 97))]

        # In[13]:

        mod_demand = (intra_demand - mustd.reindex(intra_demand.index, fill_value=0)).round(2)

        # In[14]:

        # df4=pd.read_excel(self.file_path,sheet_name="GEN_TECH_MIN_DATA",skiprows=2).drop(columns="Sl/no")
        # df4=df4[df4['Approval_No'].isna()]
        # df4=df4.groupby(by="Generator_Name").sum()[list(range(1,97))][1]
        # techmin=df4.reindex(pmax['Generator_Name'].unique(),fill_value=0)

        # In[15]:

        df4 = pd.read_excel(self.file_path, sheet_name="GEN_TECH_MIN_DATA", skiprows=2).drop(columns="Sl/no")
        df4['Approval_No'] = df4['Approval_No'].fillna("Intra State Generator")
        techmin = pd.merge(df4, pmax_mod[["Generator_Name", "Discom_Name", "Approval_No"]],
                           on=["Generator_Name", "Approval_No"])
        techmin = techmin[['Generator_Name', "Discom_Name", 'Approval_No'] + list(range(1, 97))]

        techmin1=df4[df4['Approval_No']=="Intra State Generator"].drop(columns="Approval_No")
        # In[ ]:

        # In[16]:

        df5 = pd.read_excel(self.file_path, sheet_name="GEN_ZERO_SCH", skiprows=2).drop(columns="Sl/no")
        # df5=df5.groupby(by="Generator_Name").sum()[list(range(1,97))]
        df5['Approval_No'] = df5['Approval_No'].fillna("Intra State Generator")
        # zeroschdule=df5.reindex(pmax['Generator_Name'].unique(),fill_value=0)
        df5
        zeroschdule = pd.merge(df5, pmax_mod[["Generator_Name", "Discom_Name", "Approval_No"]],
                               on=["Generator_Name", "Approval_No"])
        zeroschdule = zeroschdule[['Generator_Name', "Discom_Name", 'Approval_No'] + list(range(1, 97))]
        zeroschdule

        # In[17]:

        df4 = pd.read_excel(self.file_path, sheet_name="GEN_RAMP_UP_DATA", skiprows=2).drop(columns="Sl/no")

        df4 = df4[df4['Approval_No'].isna()]
        df4 = df4.groupby(by="Generator_Name").sum()[list(range(1, 97))][1]

        rampup = df4.reindex(pmax['Generator_Name'].unique(), fill_value=0)

        # In[18]:

        df4 = pd.read_excel(self.file_path, sheet_name="GEN_RAMP_DOWN_DATA", skiprows=2).drop(columns="Sl/no")
        df4 = df4[df4['Approval_No'].isna()]
        df4 = df4.groupby(by="Generator_Name").sum()[list(range(1, 97))][1]
        rampdown = df4.reindex(pmax['Generator_Name'].unique(), fill_value=0)

        # In[19]:

        df4 = pd.read_excel(self.file_path, sheet_name="GEN_UNIT_TRIP", skiprows=2).drop(columns="Sl/no")

        df4 = df4.groupby(by="Generator_Name").sum()[list(range(1, 97))]
        unittrip = df4.reindex(pmax['Generator_Name'].unique(), fill_value=0)

        # In[20]:

        pmax_mod = pmax_mod[
            ['Generator_Name', 'Discom_Name', 'InsgsType', 'MOD_Applicability', 'Approval_No', 'MOD_Rate'] + list(
                range(1, 97))]

        # In[21]:

        rampup1 = rampup.reset_index()
        rampup1.columns = ["Generator_Name", "Ramp"]

        temp1 = pd.merge(techmin, rampup1, on="Generator_Name", how="left")

        temp1['cool_period'] = (temp1[1] / temp1["Ramp"]).round(0).astype(int)
        temp1 = temp1[['Generator_Name', "Discom_Name", "Approval_No", "cool_period"]]

        temp2 = pd.merge(zeroschdule, temp1, on=['Generator_Name', "Discom_Name", "Approval_No"])
        temp2['sum'] = temp2[list(range(1, 97))].sum(axis=1)
        temp2 = temp2.groupby(by="Generator_Name").max()
        temp2 = temp2[temp2['sum'] > 0]
        for index, row in temp2.iterrows():
            cd = row['cool_period']
            for i in range(1, 97):
                col = 97 - i
                if row[col] == 1:
                    offset_end = min(96, col + cd + 1)
                    for offset in range(col, offset_end):
                        temp2.at[index, offset] = 1

        zeroschdule = temp2.copy()
        scalars=self.get_date_revision()
        # In[22]:

        # output_path="E:\Work\SCED\GAMS\GAMS\Python\App1/notebook/GAMS3/input.xlsx"
        writer = pd.ExcelWriter(self.output_path, )
        scalars.to_excel(writer,sheet_name="Scalars",index=True)
        mod_demand.to_excel(writer, sheet_name="DEMAND", index=True)
        pmax_mod.to_excel(writer, sheet_name="Pmax", index=True)
        techmin.to_excel(writer, sheet_name="Tech_Min", index=True)
        rampup.to_excel(writer, sheet_name="RampUP", index=True)
        rampdown.to_excel(writer, sheet_name="RampDown", index=True)
        hydro.to_excel(writer, sheet_name="Hydro", index=True)
        hydro_sc.to_excel(writer, sheet_name="Hydro_Sc", index=True)
        unittrip.to_excel(writer, sheet_name="UnitTrip", index=True)
        zeroschdule.to_excel(writer, sheet_name="ZeroSchedule", index=True)
        sc.to_excel(writer, sheet_name="Schedule", index=True)

        writer.close()