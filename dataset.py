
import kagglehub
from kagglehub import KaggleDatasetAdapter


file_path = "C:\Users\Sudharshan\Desktop\hackathon\Dataset\archive"

df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "ismetsemedov/personal-budget-transactions-dataset",
  file_path,
com/Kaggle/kagglehub/blob/main/README.md
)


print("First 5 records:", df.head())
