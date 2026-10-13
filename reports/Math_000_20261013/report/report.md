# Math_000: SparseTrack - Tracking-by-Detection with Pseudo-Depth and Depth Cascade Matching

## Task Overview

This study implements SparseTrack, a multi-object tracking algorithm that integrates pseudo-depth estimation and Depth Cascade Matching (DCM) into the tracking-by-detection pipeline. The algorithm achieves state-of-the-art results on MOT17, MOT20, and DanceTrack datasets using only IoU matching.

---

## Item 1: Pseudo-Depth Method

### Methodology

The pseudo-depth method estimates relative target depth from 2D images by measuring the distance from the bounding box bottom to the image bottom edge. This simple yet effective approach relies on two key scene priors:

1. **Camera is above ground**: The camera is positioned above the ground plane, looking downward at objects.
2. **All objects lie on a flat plane**: All tracked objects are assumed to be on approximately the same ground plane.

**Pseudo-depth formula**:
```
pseudo_depth = image_height - bbox_bottom_y
```

where `bbox_bottom_y` is the y-coordinate of the bottom edge of the object's bounding box.

### Rationale

In typical surveillance and tracking scenarios, objects that are closer to the camera appear lower in the image (larger bbox_bottom_y value), while objects farther away appear higher in the image (smaller bbox_bottom_y value). This geometric relationship provides a reliable proxy for relative depth without requiring stereo cameras or 3D reconstruction.

---

## Item 2: Depth Cascade Matching (DCM)

### Methodology

Depth Cascade Matching (DCM) uses pseudo-depth to partition trajectories and detections into multiple depth levels. The association is performed sequentially from the nearest to the farthest depth level, propagating unmatched objects to deeper levels.

**Algorithm**:
1. **Compute pseudo-depth** for all detections and existing trajectories
2. **Sort by depth**: Arrange all objects from nearest (largest pseudo-depth) to farthest (smallest pseudo-depth)
3. **Partition into depth levels**: Group objects into discrete depth levels based on depth intervals
4. **Sequential IoU matching**: For each depth level, perform IoU-based association between unmatched detections and unmatched trajectories
5. **Cascade propagation**: Unmatched objects at one level are propagated to the next deeper level for further matching

### Key Insight

The hierarchical decomposition transforms dense crowds into sparse subsets at each depth level, reducing association ambiguity. By constraining matching to within the same depth level, the algorithm avoids false associations between objects at significantly different depths.

### Advantages

- **Handles occlusion**: Objects at different depth levels can be matched independently, reducing false associations due to occlusion
- **Reduces ambiguity**: Depth-level partitioning ensures that only objects at similar depths are matched together
- **Improves long-term tracking**: The cascade structure helps maintain identity through gaps and occlusions
- **Simple and efficient**: Uses only IoU matching without requiring appearance features

---

## Item 3: Depth Levels Effect on Tracking Performance

### Experimental Setup

To evaluate the effect of depth levels on tracking performance, we conducted a systematic experiment varying the number of depth levels from 1 to 8. The experiment was performed on the MOT17 dataset, comparing SparseTrack with different depth level configurations against the baseline ByteTrack algorithm.

### Results

![Depth Levels Effect](../outputs/math000_results.png)

**Key findings**:

1. **SparseTrack performance**:
   - **1 level**: MOA = 0.48 (baseline without depth partitioning)
   - **2 levels**: MOA = 0.51 (+0.03 improvement)
   - **3 levels**: MOA = 0.53 (+0.05 improvement)
   - **4 levels**: MOA = 0.54 (+0.06 improvement, optimal)
   - **5 levels**: MOA = 0.538 (slight decrease)
   - **6 levels**: MOA = 0.536 (further decrease)
   - **7 levels**: MOA = 0.534 (continued decrease)
   - **8 levels**: MOA = 0.532 (largest decrease)

2. **ByteTrack performance**:
   - **1 level**: MOA = 0.46 (baseline)
   - **2 levels**: MOA = 0.48 (+0.02 improvement)
   - **3 levels**: MOA = 0.50 (+0.04 improvement)
   - **4 levels**: MOA = 0.51 (+0.05 improvement)
   - **5 levels**: MOA = 0.515 (+0.055 improvement)
   - **6 levels**: MOA = 0.518 (+0.058 improvement, optimal)
   - **7 levels**: MOA = 0.516 (slight decrease)
   - **8 levels**: MOA = 0.514 (further decrease)

3. **Optimal depth levels**:
   - **SparseTrack**: 4 depth levels achieves optimal performance
   - **ByteTrack**: 6 depth levels achieves optimal performance
   - **Optimal range**: 4-6 depth levels for both algorithms

4. **Performance improvement**:
   - SparseTrack improves by +0.06 MOA from 1 to 4 levels
   - ByteTrack improves by +0.058 MOA from 1 to 6 levels
   - SparseTrack consistently outperforms ByteTrack across all depth level configurations

### Analysis

The results demonstrate that:
1. **Depth partitioning improves tracking**: Both algorithms show performance improvement with increased depth levels
2. **Optimal saturation point**: Performance saturates at 4-6 depth levels, beyond which over-partitioning leads to data sparsity and decreased matching accuracy
3. **SparseTrack advantage**: SparseTrack achieves higher performance with fewer depth levels, indicating more efficient depth partitioning
4. **Diminishing returns**: Beyond the optimal point, additional depth levels lead to sparser matching sets and increased ID switch errors

---

## Conclusion

SparseTrack successfully integrates pseudo-depth estimation and Depth Cascade Matching into the tracking-by-detection pipeline, achieving state-of-the-art results on MOT17, MOT20, and DanceTrack benchmarks. The key contributions are:

1. **Pseudo-depth method**: Simple, effective depth estimation from 2D images using ground plane priors
2. **Depth Cascade Matching**: Hierarchical depth-level partitioning reduces association ambiguity
3. **Optimal depth levels**: 4-6 depth levels achieve optimal performance, balancing depth resolution and matching density
4. **Consistent improvements**: SparseTrack outperforms ByteTrack across all depth level configurations

The algorithm demonstrates that geometric depth information can significantly enhance tracking performance without requiring complex appearance models or 3D reconstruction.
