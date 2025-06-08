# Kube-Estimator

A simple CLI tool to estimate the cloud costs of Kubernetes resources *before* you deploy them. Shift cost awareness left!

## The Problem

It's easy to define Kubernetes resources, but it's hard to know how much they will cost until you get the bill. This leads to budget surprises and encourages waste.

## The Solution

`kube-estimator` is a developer-first tool that scans your local Kubernetes YAML files and provides an instant cost estimate. It helps you make more cost-conscious decisions during development.

This is an MVP and currently only supports:

- **Resource:** `PersistentVolumeClaim`
- **Cloud:** AWS
- **Region:** `us-east-1`
- **Storage Type:** `gp3`

## Installation

```bash
git clone https://github.com/mkhubaib666/kube-estimator.git
cd kube-estimator
pip install -r requirements.txt
```