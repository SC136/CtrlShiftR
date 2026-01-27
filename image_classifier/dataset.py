"""
🌾 FARMER ASSISTANT - DATASET MODULE
Handles PlantVillage dataset loading and augmentation
Heavy augmentation for mobile/field conditions
"""

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import os
from pathlib import Path
from typing import Tuple, List, Optional
import kagglehub


class PlantDiseaseDataset(Dataset):
    """
    PyTorch Dataset for PlantVillage-style datasets.
    
    Folder structure:
        dataset/
         ├── Tomato___Early_blight/
         │   ├── image1.jpg
         │   ├── image2.jpg
         ├── Tomato___Late_blight/
         └── ...
    """
    
    def __init__(self, root_dir: str, transform: Optional[transforms.Compose] = None):
        """
        Initialize dataset.
        
        Args:
            root_dir: Root directory containing class folders
            transform: Torchvision transforms to apply
        """
        self.root_dir = Path(root_dir)
        self.transform = transform
        
        # Scan directory and build class list
        self.classes = sorted([d.name for d in self.root_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # Build image paths and labels
        self.samples = []
        for class_name in self.classes:
            class_dir = self.root_dir / class_name
            class_idx = self.class_to_idx[class_name]
            
            for img_path in class_dir.glob("*.jpg"):
                self.samples.append((str(img_path), class_idx))
            for img_path in class_dir.glob("*.JPG"):
                self.samples.append((str(img_path), class_idx))
            for img_path in class_dir.glob("*.png"):
                self.samples.append((str(img_path), class_idx))
        
        print(f"✅ Dataset loaded: {len(self.samples)} images, {len(self.classes)} classes")
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_class_names(self) -> List[str]:
        """Return list of class names."""
        return self.classes


def get_train_transforms() -> transforms.Compose:
    """
    Heavy augmentation for training.
    Simulates real-world field conditions.
    """
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=30),
        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.3,
            hue=0.1
        ),
        transforms.RandomAffine(
            degrees=0,
            translate=(0.1, 0.1),
            scale=(0.8, 1.2)
        ),
        transforms.RandomApply([
            transforms.GaussianBlur(kernel_size=3)
        ], p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        transforms.RandomErasing(p=0.2)
    ])


def get_val_transforms() -> transforms.Compose:
    """
    Validation/test transforms (no augmentation).
    """
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_inference_transforms() -> transforms.Compose:
    """
    Inference transforms (same as validation).
    """
    return get_val_transforms()


def create_data_loaders(
    dataset_path: str,
    batch_size: int = 32,
    train_split: float = 0.7,
    val_split: float = 0.15,
    test_split: float = 0.15,
    num_workers: int = 4
) -> Tuple[DataLoader, DataLoader, DataLoader, List[str]]:
    """
    Create train, validation, and test data loaders.
    
    Args:
        dataset_path: Path to dataset root
        batch_size: Batch size
        train_split: Fraction for training (default 0.7)
        val_split: Fraction for validation (default 0.15)
        test_split: Fraction for testing (default 0.15)
        num_workers: Number of data loading workers
        
    Returns:
        (train_loader, val_loader, test_loader, class_names)
    """
    assert abs(train_split + val_split + test_split - 1.0) < 1e-6, "Splits must sum to 1.0"
    
    # Create datasets with transforms
    train_dataset = PlantDiseaseDataset(dataset_path, transform=get_train_transforms())
    val_dataset = PlantDiseaseDataset(dataset_path, transform=get_val_transforms())
    test_dataset = PlantDiseaseDataset(dataset_path, transform=get_val_transforms())
    
    # Get class names
    class_names = train_dataset.get_class_names()
    
    # Calculate split sizes
    total_size = len(train_dataset)
    train_size = int(train_split * total_size)
    val_size = int(val_split * total_size)
    test_size = total_size - train_size - val_size
    
    # Split datasets
    train_subset, val_subset, test_subset = random_split(
        train_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Update transforms for val and test subsets
    val_subset.dataset = val_dataset
    test_subset.dataset = test_dataset
    
    # Create data loaders
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"✅ Data loaders created:")
    print(f"   Train: {len(train_subset)} samples ({train_split*100:.0f}%)")
    print(f"   Val:   {len(val_subset)} samples ({val_split*100:.0f}%)")
    print(f"   Test:  {len(test_subset)} samples ({test_split*100:.0f}%)")
    
    return train_loader, val_loader, test_loader, class_names


def download_plantvillage_dataset() -> str:
    """
    Download PlantDisease dataset from Kaggle using kagglehub.
    
    Returns:
        Path to downloaded dataset
    """
    print("📥 Downloading PlantDisease dataset from Kaggle...")
    path = kagglehub.dataset_download("emmarex/plantdisease")
    print(f"✅ Dataset downloaded to: {path}")
    return path


if __name__ == "__main__":
    # Test dataset loading (without downloading)
    print("🧪 Testing dataset module...")
    
    # Example: Test transforms
    train_tfm = get_train_transforms()
    val_tfm = get_val_transforms()
    
    print("✅ Transforms created successfully")
    print(f"   Train transforms: {len(train_tfm.transforms)} steps")
    print(f"   Val transforms:   {len(val_tfm.transforms)} steps")
    
    # If you have a dataset path, uncomment to test:
    # dataset_path = "path/to/plantvillage"
    # train_loader, val_loader, test_loader, classes = create_data_loaders(
    #     dataset_path, batch_size=16
    # )
    # print(f"✅ Data loaders ready with {len(classes)} classes")
