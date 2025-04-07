import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="")

# Add arguments
parser.add_argument("-d","--data", type=str, help="The input data file")


# Parse arguments
args = parser.parse_args()

print(args.data)