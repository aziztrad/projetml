import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_and_preprocess_data(data_path="data/creditcard.csv", scaler_path="model/scaler.pkl"):
    # Load data
    print(" Chargement des données...")
    if not os.path.exists(data_path):
        print(f"Erreur: Le fichier de données {data_path} n'a pas été trouvé.")
        return None, None, None
        
    df = pd.read_csv(data_path)
    
    # Separate features and target
    if 'Class' not in df.columns or 'Time' not in df.columns:
        print("Erreur: Les colonnes 'Class' ou 'Time' sont manquantes dans le dataset.")
        return None, None, None
        
    X = df.drop(['Class', 'Time'], axis=1)
    y = df['Class']
    
    # Scale the features
    print(" Préparation et mise à l'échelle des données...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Ensure model directory exists
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    
    # Save the scaler
    print(f" Sauvegarde du scaler -> {scaler_path}")
    joblib.dump(scaler, scaler_path)
    
    return X_scaled, y, X.columns

def train_and_evaluate_models(X, y, features):
    print("🔧 Entraînement et évaluation des modèles...")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Define models
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
        "LinearSVC": LinearSVC(max_iter=1000, random_state=42, dual=False), # dual=False for n_samples > n_features
        "KNN": KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
    }
    
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n--- Entraînement du modèle: {name} ---")
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Evaluate model
        print(f" Évaluation du modèle: {name}")
        y_pred = model.predict(X_test)
        print("\nRapport de classification:")
        print(classification_report(y_test, y_pred))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Matrice de Confusion - {name}')
        plt.ylabel('Vraie classe')
        plt.xlabel('Classe prédite')
        cm_path = f'model/confusion_matrix_{name}.png'
        plt.savefig(cm_path)
        print(f" Matrice de confusion sauvegardée -> {cm_path}")
        plt.close()

        # Feature importance (only for Logistic Regression)
        if hasattr(model, 'coef_'):
            try:
                # For Linear models like Logistic Regression
                importance = np.abs(model.coef_[0])
                feature_importance = pd.DataFrame({
                    'feature': features,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                plt.figure(figsize=(10, 6))
                sns.barplot(x='importance', y='feature', data=feature_importance.head(10))
                plt.title(f'Top 10 Caractéristiques - {name}')
                plt.tight_layout()
                fi_path = f'model/feature_importance_{name}.png'
                plt.savefig(fi_path)
                print(f" Importance des caractéristiques sauvegardée -> {fi_path}")
                plt.close()
            except Exception as e:
                print(f"Impossible de générer l'importance des caractéristiques pour {name}: {e}")
                
    return trained_models

def save_models(models, model_dir="model"):
    print("\n Sauvegarde des modèles entraînés...")
    for name, model in models.items():
        model_path = os.path.join(model_dir, f"{name.lower()}.pkl")
        joblib.dump(model, model_path)
        print(f" -> {model_path}")

def main():
    X, y, features = load_and_preprocess_data()
    if X is None:
        return
        
    trained_models = train_and_evaluate_models(X, y, features)
    save_models(trained_models)
    
    print("\n Tous les modèles ont été entraînés et sauvegardés avec succès!")

if __name__ == "__main__":
    main()
