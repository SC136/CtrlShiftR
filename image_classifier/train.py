"""
🌾 FARMER ASSISTANT - TRAINING SCRIPT
Trains MobileNetV3-Large on PlantVillage dataset
Includes metrics, checkpointing, and early stopping
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import json
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

from model import PlantDiseaseClassifier, ClassMapper
from dataset import create_data_loaders, download_plantvillage_dataset


class Trainer:
    """
    Training manager for plant disease classifier.
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        test_loader: DataLoader,
        class_names: list,
        device: torch.device,
        output_dir: str = "output"
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.class_names = class_names
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Training state
        self.best_val_acc = 0.0
        self.epochs_without_improvement = 0
        self.history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
    
    def train_epoch(self, optimizer: optim.Optimizer, criterion: nn.Module) -> tuple:
        """Train for one epoch."""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc="Training")
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = self.model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Metrics
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, criterion: nn.Module) -> tuple:
        """Validate the model."""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc="Validation")
            for images, labels in pbar:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                pbar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'acc': f'{100.*correct/total:.2f}%'
                })
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(
        self,
        num_epochs: int = 50,
        learning_rate: float = 0.001,
        early_stopping_patience: int = 10,
        save_checkpoints: bool = True
    ):
        """
        Train the model.
        
        Args:
            num_epochs: Maximum number of epochs
            learning_rate: Initial learning rate
            early_stopping_patience: Stop if no improvement for N epochs
            save_checkpoints: Save model checkpoints
        """
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', factor=0.5, patience=5, verbose=True
        )
        
        print("\n" + "="*70)
        print("🚀 TRAINING STARTED")
        print("="*70)
        print(f"Device: {self.device}")
        print(f"Classes: {len(self.class_names)}")
        print(f"Train samples: {len(self.train_loader.dataset)}")
        print(f"Val samples: {len(self.val_loader.dataset)}")
        print(f"Epochs: {num_epochs}")
        print(f"Learning rate: {learning_rate}")
        print("="*70 + "\n")
        
        for epoch in range(1, num_epochs + 1):
            print(f"\nEpoch {epoch}/{num_epochs}")
            print("-" * 70)
            
            # Train
            train_loss, train_acc = self.train_epoch(optimizer, criterion)
            
            # Validate
            val_loss, val_acc = self.validate(criterion)
            
            # Update history
            self.history["train_loss"].append(train_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_loss"].append(val_loss)
            self.history["val_acc"].append(val_acc)
            
            # Print summary
            print(f"\n📊 Epoch {epoch} Summary:")
            print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"   Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
            
            # Learning rate scheduling
            scheduler.step(val_acc)
            
            # Save best model
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.epochs_without_improvement = 0
                
                if save_checkpoints:
                    self.save_checkpoint(epoch, "best_model.pth")
                    print(f"   ✅ New best model saved! (Val Acc: {val_acc:.2f}%)")
            else:
                self.epochs_without_improvement += 1
                print(f"   ⚠️  No improvement for {self.epochs_without_improvement} epochs")
            
            # Early stopping
            if self.epochs_without_improvement >= early_stopping_patience:
                print(f"\n⏹️  Early stopping triggered (patience: {early_stopping_patience})")
                break
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED")
        print("="*70)
        print(f"Best Val Accuracy: {self.best_val_acc:.2f}%")
        print("="*70 + "\n")
        
        # Save training history
        self.save_history()
        self.plot_history()
    
    def test(self):
        """Evaluate on test set and generate detailed metrics."""
        print("\n" + "="*70)
        print("🧪 TESTING MODEL")
        print("="*70)
        
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            pbar = tqdm(self.test_loader, desc="Testing")
            for images, labels in pbar:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                _, predicted = outputs.max(1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        
        # Calculate accuracy
        accuracy = 100. * (all_preds == all_labels).sum() / len(all_labels)
        print(f"\n📊 Test Accuracy: {accuracy:.2f}%\n")
        
        # Classification report
        print("📋 Classification Report:")
        print("-" * 70)
        report = classification_report(
            all_labels,
            all_preds,
            target_names=self.class_names,
            zero_division=0
        )
        print(report)
        
        # Save report
        report_path = self.output_dir / "classification_report.txt"
        with open(report_path, 'w') as f:
            f.write(f"Test Accuracy: {accuracy:.2f}%\n\n")
            f.write(report)
        print(f"✅ Report saved to {report_path}")
        
        # Confusion matrix
        cm = confusion_matrix(all_labels, all_preds)
        self.plot_confusion_matrix(cm)
        
        return accuracy
    
    def save_checkpoint(self, epoch: int, filename: str):
        """Save model checkpoint."""
        checkpoint_path = self.output_dir / filename
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'best_val_acc': self.best_val_acc,
            'class_names': self.class_names
        }, checkpoint_path)
    
    def save_history(self):
        """Save training history to JSON."""
        history_path = self.output_dir / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"✅ Training history saved to {history_path}")
    
    def plot_history(self):
        """Plot training curves."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Loss
        axes[0].plot(self.history["train_loss"], label="Train Loss")
        axes[0].plot(self.history["val_loss"], label="Val Loss")
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].set_title("Training and Validation Loss")
        axes[0].legend()
        axes[0].grid(True)
        
        # Accuracy
        axes[1].plot(self.history["train_acc"], label="Train Acc")
        axes[1].plot(self.history["val_acc"], label="Val Acc")
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Accuracy (%)")
        axes[1].set_title("Training and Validation Accuracy")
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plot_path = self.output_dir / "training_curves.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()
        
        print(f"✅ Training curves saved to {plot_path}")
    
    def plot_confusion_matrix(self, cm: np.ndarray):
        """Plot and save confusion matrix."""
        plt.figure(figsize=(15, 12))
        sns.heatmap(
            cm,
            annot=False,
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names
        )
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")
        plt.tight_layout()
        
        cm_path = self.output_dir / "confusion_matrix.png"
        plt.savefig(cm_path, dpi=150)
        plt.close()
        
        print(f"✅ Confusion matrix saved to {cm_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Plant Disease Classifier")
    parser.add_argument("--dataset", type=str, required=True, help="Path to dataset root")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--download", action="store_true", help="Download dataset from Kaggle")
    args = parser.parse_args()
    
    # Download dataset if requested
    if args.download:
        dataset_path = download_plantvillage_dataset()
    else:
        dataset_path = args.dataset
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Using device: {device}")
    
    # Create data loaders
    print("\n📦 Loading dataset...")
    train_loader, val_loader, test_loader, class_names = create_data_loaders(
        dataset_path,
        batch_size=args.batch_size
    )
    
    # Create model
    print(f"\n🧠 Creating model with {len(class_names)} classes...")
    model = PlantDiseaseClassifier(num_classes=len(class_names), pretrained=True)
    
    # Create class mapper and save
    mapper = ClassMapper(class_names)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    mapper.save(str(output_dir / "class_map.json"))
    print(f"✅ Class mappings saved to {output_dir / 'class_map.json'}")
    
    # Train
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        class_names=class_names,
        device=device,
        output_dir=args.output
    )
    
    trainer.train(
        num_epochs=args.epochs,
        learning_rate=args.lr,
        early_stopping_patience=10
    )
    
    # Test
    trainer.test()
    
    print("\n🎉 All done! Check the output directory for results.")


if __name__ == "__main__":
    main()
